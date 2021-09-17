import asyncio
import os
import random
from collections import defaultdict

import nest_asyncio
import aiocron
import discord

from constants import FANTASY_NFL_ROOT_URL
from nfl_fantasy import League

nest_asyncio.apply()  # allow nested asyncio event loops
league = League(os.getenv('LEAGUE_ID'), int(os.getenv('LEAGUE_YEAR')))
client = discord.Client()


@client.event
async def on_ready():
    print("bot started...")
    await get_channel().send("```{}```".format(league.power_rankings()))


@client.event
async def on_message(message):
    print(message)
    print(message.content)
    print(message.mentions)
    print('----------------')


def get_channel():
    guild = client.get_guild(id=int(os.getenv('GUILD_ID')))
    channel = guild.get_channel(int(os.getenv('CHANNEL_ID')))
    return channel


def refresh_data():
    print('blocking shit...')
    asyncio.get_event_loop().run_until_complete(league.fetch_league())
    print('done')


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


@aiocron.crontab("30 16 * * 0")
async def get_projected_scoreboard():
    refresh_data()

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


@aiocron.crontab("30 8 * * 2")
async def get_standings():
    refresh_data()

    standings = sorted(league.teams.values(), key=lambda team: team.standing, reverse=False)
    url = "{}/league/{}".format(FANTASY_NFL_ROOT_URL, league.league_id)
    embed = discord.Embed(title="League Standings", url=url)
    embed.color = 0x9b9b9b
    for team in standings:
        value_str = '_\tPoints For: {}\n\tPoints Against: {}_'.format(team.points_for, team.points_against)
        embed.add_field(name='**{}. {}** ({}-{}-{})'.format(team.standing, team.team_name, team.wins, team.losses, team.ties), value=value_str, inline=False)
    await get_channel().send(embed=embed)


@aiocron.crontab("30 8 * * *")
async def get_recent_transactions():
    refresh_data()

    recent_drops = await league.recent_drops()
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

    recent_adds = await league.recent_adds()
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


def top_half_wins(league, top_half_totals, week):
    box_scores = league.box_scores(week=week)

    scores = [(i.home_score, i.home_team.team_name) for i in box_scores] + \
             [(i.away_score, i.away_team.team_name) for i in box_scores if i.away_team]

    scores = sorted(scores, key=lambda tup: tup[0], reverse=True)

    for i in range(0, len(scores) // 2):
        points, team_name = scores[i]
        top_half_totals[team_name] += 1

    return top_half_totals


def get_projected_total(lineup):
    total_projected = 0
    for i in lineup:
        if i.slot_position != 'BE' and i.slot_position != 'IR':
            if i.points != 0 or i.game_played > 0:
                total_projected += i.points
            else:
                total_projected += i.projected_points
    return total_projected


def all_played(lineup):
    for i in lineup:
        if i.slot_position != 'BE' and i.slot_position != 'IR' and i.game_played < 100:
            return False
    return True


def get_close_scores(league, week=None):
    # Gets current closest scores (15.999 points or closer)
    matchups = league.box_scores(week=week)
    score = []

    for i in matchups:
        if i.away_team:
            diffScore = i.away_score - i.home_score
            if (-16 < diffScore <= 0 and not all_played(i.away_lineup)) or (0 <= diffScore < 16 and not all_played(i.home_lineup)):
                score += ['%s %.2f - %.2f %s' % (i.home_team.team_abbrev, i.home_score,
                                                 i.away_score, i.away_team.team_abbrev)]
    if not score:
        return ('')
    text = ['Close Scores'] + score
    return '\n'.join(text)


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


def get_trophies(league, week=None):
    # Gets trophies for highest score, lowest score, closest score, and biggest win
    matchups = league.box_scores(week=week)
    low_score = 9999
    low_team_name = ''
    high_score = -1
    high_team_name = ''
    closest_score = 9999
    close_winner = ''
    close_loser = ''
    biggest_blowout = -1
    blown_out_team_name = ''
    ownerer_team_name = ''

    for i in matchups:
        if i.home_score > high_score:
            high_score = i.home_score
            high_team_name = i.home_team.team_name
        if i.home_score < low_score:
            low_score = i.home_score
            low_team_name = i.home_team.team_name
        if i.away_score > high_score:
            high_score = i.away_score
            high_team_name = i.away_team.team_name
        if i.away_score < low_score:
            low_score = i.away_score
            low_team_name = i.away_team.team_name
        if i.away_score - i.home_score != 0 and \
                abs(i.away_score - i.home_score) < closest_score:
            closest_score = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                close_winner = i.home_team.team_name
                close_loser = i.away_team.team_name
            else:
                close_winner = i.away_team.team_name
                close_loser = i.home_team.team_name
        if abs(i.away_score - i.home_score) > biggest_blowout:
            biggest_blowout = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                ownerer_team_name = i.home_team.team_name
                blown_out_team_name = i.away_team.team_name
            else:
                ownerer_team_name = i.away_team.team_name
                blown_out_team_name = i.home_team.team_name

    low_score_str = ['Low score: %s with %.2f points' % (low_team_name, low_score)]
    high_score_str = ['High score: %s with %.2f points' % (high_team_name, high_score)]
    close_score_str = ['%s barely beat %s by a margin of %.2f' % (close_winner, close_loser, closest_score)]
    blowout_str = ['%s blown out by %s by a margin of %.2f' % (blown_out_team_name, ownerer_team_name, biggest_blowout)]

    text = ['Trophies of the week:'] + low_score_str + high_score_str + close_score_str + blowout_str
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
