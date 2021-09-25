import asyncio
import re

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from constants import SCHEDULE, INACTIVE_INJURY_DESIGNATIONS
from nfl_fantasy import League
import json
from collections import defaultdict
import pytz
import os

tz = pytz.timezone('US/Eastern') if os.getenv('TZ') is None else pytz.timezone(os.getenv('TZ'))


async def get_record():
    url = "https://survivor.fantasy.nfl.com/group/101734"
    # async with ClientSession() as session:
    #     async with session.get(url) as response:
    #         page = await response.read()
    #         soup = BeautifulSoup(page, 'lxml')
    #
    #         transactions_table = soup.find(id="leagueTransactions").find(lambda tag: tag.name == 'tbody')
    #         rows = transactions_table.findAll(lambda tag: tag.name == 'tr')
    #         for row in rows:
    #             date_str = row.find("td", attrs={"class": re.compile(r'^transactionDate*')}).text.strip()
    #             date_str = "{}".format(date_str)
    #             date = datetime.strptime(date_str, '%b %d, %I:%M%p')
    #             print(date)
    #             if(date.month >= 9):
    #                 date = date.replace(year=2021)
    #             else:
    #                 date = date.replace(year=2022)
    #
    #             now = datetime.now()
    #             if now - timedelta(hours=24) <= date <= now:
    #                 team_tag = row.find("a", attrs={"class": re.compile(r'^teamName*')})
    #                 team_name = team_tag.text.strip()
    #                 team_id = team_tag['href'].split('/')[-1]
    #                 player_name = row.find("a", attrs={"class": re.compile(r'^playerCard playerName playerNameFull*')}).text.strip()
    #                 faab = row.find("td", attrs={"class": re.compile(r'^transactionTo$')}).text
    #                 faab = re.search("\((\d{1,}) pts\)", faab)
    #                 points_spent = 0
    #                 if(faab is not None):
    #                     points_spent = int(faab.group(1))
    #                 print("{} {} {} {} {}".format(date, team_name, player_name, points_spent, team_id))


async def lock_test(league):
    a = await league.recent_adds()
    d = await league.recent_drops()
    print(a)
    print(d)
    await league.fetch_league()
    a = await league.recent_adds()
    d = await league.recent_drops()
    print(a)
    print(d)


if __name__ == '__main__':
    # asyncio.run(lock_test())
    league = League(614261, 2021, debug=True)

    data_json = json.load(open('./ff_bot/week3_schedule.json'))
    games = data_json['events']
    games[0]['date'] = '2021-09-25T17:29Z'

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
    print(managers_screwups)

