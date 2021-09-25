import re
import threading

from aiohttp import ClientSession
import time
import asyncio
from bs4 import BeautifulSoup
from pytz import timezone

from logger import Logger
from team import Team
from typing import Tuple
from constants import FANTASY_NFL_ROOT_URL, PRO_TEAM_NAMES
from util import WebScraper
from matchup import Matchup
from playoffs import PlayoffPredictor, SlimTeam
from datetime import datetime, timedelta


# all the bot needs are box_scores, current_week, teams, power_rankings implementations for now
class League:
    """Creates a League instance for public nfl league"""

    def __init__(self, league_id: int, year: int, fetch=True, debug=False):
        self.logger = Logger(name='ffl', debug=debug)
        self.year = year
        self.league_id = league_id
        self.league_size = 12
        self.teams = {}
        self.matchups = []
        self.current_week = None
        self.lock = threading.Lock()
        if fetch:
            print("fetching data...")
            asyncio.get_event_loop().run_until_complete(self.fetch_league())

    async def fetch_league(self):
        try:
            self.lock.acquire()
            init_start_time = time.time()

            self.teams = {}
            self.matchups = []

            # from the league home page get the number of teams, the links for each team, and the current week
            league_url = '{}/league/{}'.format(FANTASY_NFL_ROOT_URL, self.league_id)
            async with ClientSession() as session:
                async with session.get(league_url) as response:
                    page = await response.read()
                    soup = BeautifulSoup(page, 'lxml')

                    # get the league size
                    standings_table = soup.find(id="leagueHomeStandings")
                    table = standings_table.find(lambda tag: tag.name == 'tbody')
                    rows = table.findAll(lambda tag: tag.name == 'tr')
                    self.league_size = len(rows)

                    # get the current week from the page
                    scoring_strip = soup.find("div", attrs={"id": "leagueHomeScoreStrip"})
                    current_week = scoring_strip \
                        .find("ul", attrs={"class": re.compile(r"^weekNav")}) \
                        .find("li", attrs={"href": None}).text \
                        .split(" ")[1]
                    self.current_week = int(current_week)

                    # get the matchup urls
                    matchup_tags = scoring_strip \
                        .find("div", attrs={"class": "teamNav"}) \
                        .find_all("a")
                    for matchup_url in matchup_tags:
                        # hrefs.append("{}{}".format(FANTASY_NFL_ROOT_URL, matchup_url['href']))
                        self.matchups.append(Matchup("{}{}".format(FANTASY_NFL_ROOT_URL, matchup_url['href'])))

                    # get the urls, fab, pts for, and pts against for each team
                    for row in rows:
                        url = '{}{}'.format(FANTASY_NFL_ROOT_URL, row.find("a", attrs={"class": re.compile(r'^teamName*')})['href'])
                        name = row.find("a", attrs={"class": re.compile(r'^teamName*')}).text.strip()
                        standing = int(row.find("span", attrs={"class": re.compile(r'^teamRank teamId-\d{1,}$')}).text.strip())

                        record = row.find("td", attrs={"class": re.compile(r'^teamRecord*')}).text.strip().split('-')
                        wins = int(record[0])
                        losses = int(record[1])
                        ties = int(record[2])

                        if not standing:
                            standing = 1
                        fab = float(row.find("td", attrs={"class": re.compile(r'^teamWaiverBudget*')}).text.strip())
                        pts_for = float(row.find("td", attrs={"class": re.compile(r'^teamPts teamPtsSort stat numeric$')}).text.strip())
                        pts_against = float(row.find("td", attrs={"class": re.compile(r'^teamPts teamPtsSort stat numeric last$')}).text.strip())
                        team_id = int(url.split('/')[-1])
                        team = Team(team_id, url, name, standing, fab, pts_for, pts_against, wins, losses, ties)
                        self.teams[team_id] = team
                    await WebScraper.fetch_team(self.teams.values())
                    await WebScraper.fetch_matchups(self.matchups, self.teams)

                    # load players for each team
                    tasks = []
                    for team in self.teams.values():
                        tasks.append(asyncio.create_task(WebScraper.fetch_players(team.roster)))
                    await asyncio.gather(*tasks)

            print(time.time() - init_start_time)
        except Exception as err:
            raise err
        finally:
            self.lock.release()

    def power_rankings(self):
        '''Return power rankings for any week'''
        try:
            self.lock.acquire()
            power = {}
            for team_id in self.teams.keys():
                team = self.teams[team_id]
                sorted_qbs = sorted(filter(lambda player: player.pos == 'QB', team.roster), key=lambda player: player.get_points_total())
                sorted_rbs = sorted(filter(lambda player: player.pos == 'RB', team.roster), key=lambda player: player.get_points_total())
                sorted_wrs = sorted(filter(lambda player: player.pos == 'WR', team.roster), key=lambda player: player.get_points_total())
                sorted_tes = sorted(filter(lambda player: player.pos == 'TE', team.roster), key=lambda player: player.get_points_total())
                sorted_dst = sorted(filter(lambda player: player.pos == 'DEF', team.roster), key=lambda player: player.get_points_total())
                flex_options = []
                if (len(sorted_tes) > 1):
                    flex_options.append(sorted_tes[1])
                if (len(sorted_wrs) > 2):
                    flex_options.append(sorted_wrs[2])
                if (len(sorted_rbs) > 2):
                    flex_options.append(sorted_rbs[2])
                flex = sorted(flex_options, key=lambda player: player.get_points_total())

                starting_lineup = [sorted_qbs[0], sorted_rbs[0], sorted_rbs[1], sorted_wrs[0], sorted_wrs[1], sorted_tes[0], flex, sorted_dst[0]]
                team_power = sum(player.get_points_total() for player in starting_lineup)
                power[team_id] = team_power
            return power
        except Exception as err:
            raise err
        finally:
            self.lock.release()

    async def recent_adds(self):
        try:
            print("acquiring lock...")
            self.lock.acquire()
            adds_url = "{}/league/{}/transactions?transactionType=add".format(FANTASY_NFL_ROOT_URL, self.league_id)
            return await self.parse_transactions(self.teams, self.year, adds_url, faab_on=True)
        except Exception as err:
            raise err
        finally:
            print('releasing lock')
            self.lock.release()

    async def recent_drops(self):
        try:
            print("acquiring lock...")
            self.lock.acquire()
            drops_url = "{}/league/{}/transactions?transactionType=drop".format(FANTASY_NFL_ROOT_URL, self.league_id)
            return await self.parse_transactions(self.teams, self.year, drops_url, faab_on=False)
        except Exception as err:
            raise err
        finally:
            print('releasing lock')
            self.lock.release()

    @staticmethod
    async def parse_transactions(teams, year, url, faab_on=True):
        try:
            async with ClientSession() as session:
                async with session.get(url) as response:
                    page = await response.read()
                    soup = BeautifulSoup(page, 'lxml')

                    transactions_table = soup.find(id="leagueTransactions").find(lambda tag: tag.name == 'tbody')
                    rows = transactions_table.findAll(lambda tag: tag.name == 'tr')
                    table_rows = []
                    for row in rows:
                        date_str = row.find("td", attrs={"class": re.compile(r'^transactionDate*')}).text.strip()
                        date_str = "{}".format(date_str)
                        date = datetime.strptime(date_str, '%b %d, %I:%M%p').replace(tzinfo=timezone('US/Pacific')) # NFL.com dates are in westcoast time
                        if date.month < 9:
                            date = date.replace(year=year + 1)
                        else:
                            date = date.replace(year=year)

                        now = datetime.now().replace(tzinfo=timezone('US/Eastern'))
                        if (now - timedelta(hours=24) <= date <= now):
                            team_pos = row.find("em").text.strip().split('-')[0].strip()
                            team_tag = row.find("a", attrs={"class": re.compile(r'^teamName*')})
                            team_name = team_tag.text.strip()
                            team_id = int(team_tag['href'].split('/')[-1])
                            player_name = row.find("a", attrs={"class": re.compile(r'^playerCard playerName playerNameFull*')}).text.strip()
                            if (faab_on):
                                faab = row.find("td", attrs={"class": re.compile(r'^transactionTo$')}).text
                                faab = re.search("\((\d{1,}) pts\)", faab)
                                points_spent = 0
                                if (faab is not None):
                                    points_spent = int(faab.group(1))
                                table_rows.append([points_spent, teams[team_id].faab, team_pos, player_name, team_name])
                            else:
                                table_rows.append([team_pos, player_name, team_name])
                    return table_rows
        except Exception as err:
            raise err

    # def playoff_picture(self):
    #     try:
    #         self.lock.acquire()
    #         slim_teams = {}
    #         for team_id in self.teams.keys():
    #             slim_teams[team_id] = SlimTeam(self.teams[team_id])
    #         predictor = PlayoffPredictor(slim_teams)
    #         start_time = time.time()
    #         predictor.simulate_outcomes()
    #         print(time.time() - start_time)
    #     except Exception as err:
    #         raise err
    #     finally:
    #         self.lock.release()
    #
    # def top_scorer(self) -> Team:
    #     most_pf = sorted(self.teams, key=lambda x: x.points_for, reverse=True)
    #     return most_pf[0]
    #
    # def least_scorer(self) -> Team:
    #     least_pf = sorted(self.teams, key=lambda x: x.points_for, reverse=False)
    #     return least_pf[0]
    #
    # def most_points_against(self) -> Team:
    #     most_pa = sorted(self.teams, key=lambda x: x.points_against, reverse=True)
    #     return most_pa[0]
    #
    # def top_scored_week(self) -> Tuple[Team, int]:
    #     top_week_points = []
    #     for team in self.teams:
    #         top_week_points.append(max(team.scores[:self.current_week]))
    #     top_scored_tup = [(i, j) for (i, j) in zip(self.teams, top_week_points)]
    #     top_tup = sorted(top_scored_tup, key=lambda tup: int(tup[1]), reverse=True)
    #     return top_tup[0]
    #
    # def least_scored_week(self) -> Tuple[Team, int]:
    #     least_week_points = []
    #     for team in self.teams:
    #         least_week_points.append(min(team.scores[:self.current_week]))
    #     least_scored_tup = [(i, j) for (i, j) in zip(self.teams, least_week_points)]
    #     least_tup = sorted(least_scored_tup, key=lambda tup: int(tup[1]), reverse=False)
    #     return least_tup[0]
    #
    # def get_team_data(self, team_id: int) -> Team:
    #     for team in self.teams:
    #         if team_id == team.team_id:
    #             return team
    #     return None

    @staticmethod
    def abbr_player_name(player_name):
        if player_name.title() in PRO_TEAM_NAMES:
            abbr_name = player_name.title().split(' ')[-1]
        else:
            abbr_name = "{}. {}".format(player_name[0], player_name.split(' ')[-1])

        return (abbr_name[:12].strip() + '.') if len(abbr_name) > 12 else abbr_name

    @staticmethod
    def abbr_team_name(team_name):
        return (team_name[:12].strip() + '.') if len(team_name) > 12 else team_name
