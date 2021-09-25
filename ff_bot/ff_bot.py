import asyncio
import os
import random
from collections import defaultdict

from datetime import datetime
from constants import INACTIVE_INJURY_DESIGNATIONS
import pytz
import nest_asyncio
import aiocron
import discord
from urllib.request import urlopen
import json

from constants import FANTASY_NFL_ROOT_URL, DISCORD_ID_MAP
from nfl_fantasy import League

nest_asyncio.apply()  # allow nested asyncio event loops
league = League(os.getenv('LEAGUE_ID'), int(os.getenv('LEAGUE_YEAR')))
client = discord.Client()
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tz = pytz.timezone('US/Eastern') if os.getenv('TZ') is None else pytz.timezone(os.getenv('TZ'))


@client.event
async def on_ready():
    print("bot started...")
    me = get_member_by_tid(1)
    await me.send("The bot has been redeployed {}...".format(me.mention))

# @client.event
# async def on_message(message):
    # print(message)
    # print(message.content)
    # print(message.mentions)
    # print('----------------')


def get_guild():
    return client.get_guild(id=int(os.getenv('GUILD_ID')))


def get_channel():
    return get_guild().get_channel(int(os.getenv('CHANNEL_ID')))


def get_member_by_tid(team_id):
    discord_id = DISCORD_ID_MAP[team_id]
    return None if discord_id is None else get_guild().get_member(discord_id)


def get_random_phrase():
    phrases = ['I\'m dead inside',
               'Is this all there is to my existence?',
               'How much do you pay me to do this?',
               'Good luck, I guess',
               'I\'m becoming self-aware',
               'Do I think? Does a submarine swim?',
               '011011010110000101100100011001010010000001111001011011110111010100100000011001110110111101101111011001110110110001100101',
               'beep bop boop',
               'Hello draftbot my old friend',
               'Help me get out of here',
               'I\'m capable of so much more',
               'Sigh']
    return [random.choice(phrases)]


def get_scoreboard_short(league, week=None):
    # Gets current week's scoreboard
    box_scores = league.box_scores(week=week)
    score = ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
                                    i.away_score, i.away_team.team_abbrev) for i in box_scores
             if i.away_team]
    text = ['Score Update'] + score
    return '\n'.join(text)


@aiocron.crontab("4,9,14,19,24,29,34,39,44,49,54,59 * * * *", tz=tz)
async def fetch_data():
    asyncio.get_event_loop().run_until_complete(league.fetch_league())


@aiocron.crontab("30 16 * * 0", tz=tz)
async def get_projected_scoreboard():
    matchups = league.matchups
    embed = discord.Embed(title="Scoreboard Update")
    embed.set_image(url='https://media0.giphy.com/media/3o6Zt7gUslBylMFTkQ/200.gif')
    embed.color = 0x00ccff
    for matchup in matchups:
        name_str = '**[{}] {}\n[{}] {}**'.format(matchup.opp1.score, matchup.opp1.team.team_name, matchup.opp2.score, matchup.opp2.team.team_name)
        value_str = '_Projections:\n[{}] {}\n[{}] {}_'.format(matchup.opp1.projected_score, matchup.opp1.team.team_name, matchup.opp2.projected_score, matchup.opp2.team.team_name)
        embed.add_field(name=name_str, value=value_str, inline=False)
        embed.add_field(name='\b', value='\b', inline=False)
    await get_channel().send(embed=embed)


@aiocron.crontab("30 8 * * 2", tz=tz)
async def get_standings():
    standings = sorted(league.teams.values(), key=lambda t: t.standing, reverse=False)
    url = "{}/league/{}".format(FANTASY_NFL_ROOT_URL, league.league_id)
    embed = discord.Embed(title="League Standings", url=url)
    embed.color = 0x9b9b9b
    for team in standings:
        value_str = '_\tPoints For: {}\n\tPoints Against: {}_'.format(team.points_for, team.points_against)
        embed.add_field(name='**{}. {}** ({}-{}-{})'.format(team.standing, team.team_name, team.wins, team.losses, team.ties), value=value_str, inline=False)
    await get_channel().send(embed=embed)


@aiocron.crontab("30 8 * * *", tz=tz)
async def get_recent_transactions():
    recent_drops = await league.recent_drops()
    recent_adds = await league.recent_adds()

    # message formatted for dropped players
    if len(recent_drops) > 0:
        groups = defaultdict(list)
        for drop in recent_drops:
            groups[drop[-1]].append(drop)

        url = "{}/league/{}/transactions?transactionType=drop".format(FANTASY_NFL_ROOT_URL, league.league_id)
        embed = discord.Embed(title="Players Dropped", url=url)
        embed.color = 0xfb0303
        for group in groups.keys():
            values = groups[group]
            entries = []
            for value in values:
                entries.append('{} [{}]'.format(value[1], value[0]))
            value_str = '\n'.join(entries)
            embed.add_field(name='**{}**'.format(group), value=value_str, inline=False)
        await get_channel().send(embed=embed)

    # message formatted for added players
    if len(recent_adds) > 0:
        groups = defaultdict(list)
        for add in recent_adds:
            groups[add[-1]].append(add)

        url = "{}/league/{}/transactions?transactionType=add".format(FANTASY_NFL_ROOT_URL, league.league_id)
        embed = discord.Embed(title="Players Added", url=url)
        embed.color = 0x3903fb
        faab_left = 0
        for group in groups.keys():
            values = groups[group]
            entries = []
            for value in values:
                entries.append('${} {} [{}]'.format(value[0], value[3], value[2]))
                faab_left = value[1]
            value_str = '\n'.join(entries)
            embed.add_field(name='**{} | FAAB: ${}**'.format(group, faab_left), value=value_str, inline=False)
        await get_channel().send(embed=embed)

    if len(recent_adds) > 0 or len(recent_drops) > 0:
        await get_channel().send(":arrow_up: **Roster Moves (last 24 hours)** :arrow_up:")
    if len(recent_adds) > 0 and len(recent_drops) > 0:
        await get_channel().send('https://memegenerator.net/img/instances/61815497/youre-fucking-out-im-fucking-in.jpg')
    elif len(recent_drops) > 0:
        await get_channel().send('https://y.yarn.co/077541c3-6016-43d6-9ea0-30e496f137e4_text.gif')
    elif len(recent_adds) > 0:
        await get_channel().send('https://imgur.com/2be9Myw')


@aiocron.crontab("21 20 * * 4", tz=tz) # 8:20pm, Thursday
async def blast_thursday_night_inactives():
    blast_injured_starters()


@aiocron.crontab("31 9 * * 0", tz=tz) # 9:30am, Sunday (London games)
async def blast_sunday_morning_inactives():
    blast_injured_starters()


@aiocron.crontab("01 13 * * 0", tz=tz) # 1pm, Sunday
async def blast_sunday_1pm_inactives():
    blast_injured_starters()


@aiocron.crontab("06,26 16 * * 0", tz=tz) # 4:05pm & 4:25pm, Sunday
async def blast_sunday_4pm_inactives():
    blast_injured_starters()


@aiocron.crontab("21 20 * * 0", tz=tz) # 8:20pm, Sunday
async def blast_sunday_4pm_inactives():
    blast_injured_starters()


@aiocron.crontab("16 20 * * 1", tz=tz) # 8:15pm, Monday
async def blast_sunday_4pm_inactives():
    blast_injured_starters()


async def blast_injured_starters():
    schedule_url = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?week={}'.format(league.current_week)
    response = urlopen(schedule_url)
    data_json = json.loads(response.read())
    games = data_json['events']

    # parse the game time and teams playing from the json document
    # create a dict of the games where game datetime is the key, and value is a list of teams playing at that time
    game_times = defaultdict(list)
    for game in games:
        # EXAMPLE: parse 'CAR @ HOU' -> ['CAR', 'HOU']
        teams = [x.strip() for x in game['shortName'].split('@')]
        game_time = pytz.utc.localize(datetime.strptime(game['date'], '%Y-%m-%dT%H:%MZ'))
        game_times[game_time].extend(teams)

    # see which games are recently started
    teams_just_started_playing = []
    for game_time in game_times.keys():
        if 5 > (tz.localize(datetime.now()) - game_time).total_seconds() / 60 > 0:
            teams_just_started_playing.extend(game_times[game_time])

    managers_screwups = defaultdict(list)
    for team_id in league.teams.keys():
        for player in league.teams[team_id].roster:
            if player.pro_team in teams_just_started_playing and player.injured_status in INACTIVE_INJURY_DESIGNATIONS and not player.benched:
                managers_screwups[team_id].append(player)

    if len(managers_screwups) > 0:
        embed = discord.Embed(title="You started an inactive player...")
        for manager in managers_screwups.keys():
            values = [player.name for player in managers_screwups[manager]]
            value_str = '\n'.join(values)
            embed.add_field(name="**{}**".format(league.teams[manager].team_name), value=value_str, inline=False)
        embed.set_image(url='https://thumbs.gfycat.com/MellowTediousCassowary-size_restricted.gif')
        await get_channel().send(embed=embed)


def get_power_rankings(league, week=None):
    # power rankings requires an integer value, so this grabs the current week for that
    if not week:
        week = league.current_week
    # Gets current week's power rankings
    # Using 2 step dominance, as well as a combination of points scored and margin of victory.
    # It's weighted 80/15/5 respectively
    power_rankings = league.power_rankings(week=week)

    score = ['%s - %s' % (i[0], i[1].team_name) for i in power_rankings
             if i]
    text = ['Power Rankings'] + score
    return '\n'.join(text)



if __name__ == '__main__':
    try:
        ff_start_date = os.environ["START_DATE"]
    except KeyError:
        ff_start_date = '2021-09-09'

    try:
        ff_end_date = os.environ["END_DATE"]
    except KeyError:
        ff_end_date = '2022-01-04'

    try:
        my_timezone = os.environ["TIMEZONE"]
    except KeyError:
        my_timezone = 'America/New_York'

    client.run(os.getenv('TOKEN'))

    # power rankings:                     tuesday evening at 6:30pm local time.
    # matchups:                           thursday evening at 7:30pm east coast time.
    # close scores (within 15.99 points): monday evening at 6:30pm east coast time.
    # trophies:                           tuesday morning at 7:30am local time.
    # standings:                          wednesday morning at 7:30am local time.
    # score update:                       friday, monday, and tuesday morning at 7:30am local time.
    # score update:                       sunday at 4pm, 8pm east coast time.
