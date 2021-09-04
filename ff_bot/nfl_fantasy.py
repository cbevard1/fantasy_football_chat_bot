import re
from aiohttp import ClientSession
import time
import asyncio
from bs4 import BeautifulSoup
from .logger import Logger
from .team import Team
from typing import List, Tuple
from .constants import FANTASY_NFL_ROOT_URL, HEADERS
from .util import WebScraper
from .matchup import Matchup


# all the bot needs are box_scores, current_week, teams, power_rankings implementations for now
class League:
    """Creates a League instance for public nfl league"""

    def __init__(self, league_id: int, debug=False):
        init_start_time = time.time()
        self.logger = Logger(name='ffl', debug=debug)
        self.league_id = league_id
        self.league_size = 12
        self.teams = []
        self.matchups = []
        asyncio.run(self._fetch_league())
        print(time.time() - init_start_time)

    async def _fetch_league(self):
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
                self.nfl_week = int(current_week)

                # get the matchup urls
                matchup_tags = scoring_strip\
                    .find("div", attrs={"class": "teamNav"})\
                    .find_all("a")
                for matchup_url in matchup_tags:
                    # hrefs.append("{}{}".format(FANTASY_NFL_ROOT_URL, matchup_url['href']))
                    self.matchups.append(Matchup("{}{}".format(FANTASY_NFL_ROOT_URL, matchup_url['href'])))

                # get the urls, fab, pts for, and pts against for each team
                for row in rows:
                    url = '{}{}'.format(FANTASY_NFL_ROOT_URL, row.find("a", attrs={"class": re.compile(r'^teamName*')})['href'])
                    name = row.find("a", attrs={"class": re.compile(r'^teamName*')}).text.strip()
                    standing = row.find("td", attrs={"class": re.compile(r'^teamRank*')}).text.strip()
                    if(standing is ''):
                        standing = 1
                    fab = 0#float(row.find("td", attrs={"class": re.compile(r'^teamWaiverBudget*')}).text.strip()) TODO put back
                    pts_for = float(row.find("td", attrs={"class": re.compile(r'^teamPts teamPtsSort stat numeric$')}).text.strip())
                    pts_against = float(row.find("td", attrs={"class": re.compile(r'^teamPts teamPtsSort stat numeric last$')}).text.strip())
                    team = Team(url, name, standing, fab, pts_for, pts_against)
                    self.teams.append(team)
                await WebScraper.fetch_team(self.teams)
                await WebScraper.fetch_matchups(self.matchups)

                # load players for each team
                tasks = []
                for team in self.teams:
                    tasks.append(asyncio.create_task(WebScraper.fetch_players(team.roster)))
                await asyncio.gather(*tasks)

    def _get_positional_ratings(self, week: int):
        params = {
            'view': 'mPositionalRatings',
            'scoringPeriodId': week,
        }
        data = self.espn_request.league_get(params=params)
        ratings = data.get('positionAgainstOpponent', {}).get('positionalRatings', {})

        positional_ratings = {}
        for pos, rating in ratings.items():
            teams_rating = {}
            for team, data in rating['ratingsByOpponent'].items():
                teams_rating[team] = data['rank']
            positional_ratings[pos] = teams_rating
        return positional_ratings

    def refresh(self):
        '''Gets latest league data. This can be used instead of creating a new League class each week'''
        self.teams = []
        self.matchups = []
        asyncio.run(self._fetch_league())

    def standings(self) -> List[Team]:
        standings = sorted(self.teams, key=lambda x: x.final_standing if x.final_standing != 0 else x.standing, reverse=False)
        return standings

    def top_scorer(self) -> Team:
        most_pf = sorted(self.teams, key=lambda x: x.points_for, reverse=True)
        return most_pf[0]

    def least_scorer(self) -> Team:
        least_pf = sorted(self.teams, key=lambda x: x.points_for, reverse=False)
        return least_pf[0]

    def most_points_against(self) -> Team:
        most_pa = sorted(self.teams, key=lambda x: x.points_against, reverse=True)
        return most_pa[0]

    def top_scored_week(self) -> Tuple[Team, int]:
        top_week_points = []
        for team in self.teams:
            top_week_points.append(max(team.scores[:self.current_week]))
        top_scored_tup = [(i, j) for (i, j) in zip(self.teams, top_week_points)]
        top_tup = sorted(top_scored_tup, key=lambda tup: int(tup[1]), reverse=True)
        return top_tup[0]

    def least_scored_week(self) -> Tuple[Team, int]:
        least_week_points = []
        for team in self.teams:
            least_week_points.append(min(team.scores[:self.current_week]))
        least_scored_tup = [(i, j) for (i, j) in zip(self.teams, least_week_points)]
        least_tup = sorted(least_scored_tup, key=lambda tup: int(tup[1]), reverse=False)
        return least_tup[0]

    def get_team_data(self, team_id: int) -> Team:
        for team in self.teams:
            if team_id == team.team_id:
                return team
        return None

    # def recent_activity(self, size: int = 25, msg_type: str = None) -> List[Activity]:
    #     '''Returns a list of recent league activities (Add, Drop, Trade)'''
    #     if self.year < 2019:
    #         raise Exception('Cant use recent activity before 2019')
    #
    #     msg_types = [178,180,179,239,181,244]
    #     if msg_type in ACTIVITY_MAP:
    #         msg_types = [ACTIVITY_MAP[msg_type]]
    #     params = {
    #         'view': 'kona_league_communication'
    #     }
    #
    #     filters = {"topics":{"filterType":{"value":["ACTIVITY_TRANSACTIONS"]},"limit":size,"limitPerMessageSet":{"value":25},"offset":0,"sortMessageDate":{"sortPriority":1,"sortAsc":False},"sortFor":{"sortPriority":2,"sortAsc":False},"filterIncludeMessageTypeIds":{"value":msg_types}}}
    #     headers = {'x-fantasy-filter': json.dumps(filters)}
    #     data = self.espn_request.league_get(extend='/communication/', params=params, headers=headers)
    #     data = data['topics']
    #     activity = [Activity(topic, self.player_map, self.get_team_data, self.player_info) for topic in data]
    #
    #     return activity

    # def scoreboard(self, week: int = None) -> List[Matchup]:
    #     '''Returns list of matchups for a given week'''
    #     if not week:
    #         week = self.current_week
    #
    #     params = {
    #         'view': 'mMatchupScore',
    #     }
    #     data = self.espn_request.league_get(params=params)
    #
    #     schedule = data['schedule']
    #     matchups = [Matchup(matchup) for matchup in schedule if matchup['matchupPeriodId'] == week]
    #
    #     for team in self.teams:
    #         for matchup in matchups:
    #             if matchup.home_team == team.team_id:
    #                 matchup.home_team = team
    #             elif matchup.away_team == team.team_id:
    #                 matchup.away_team = team
    #
    #     return matchups

    # def box_scores(self, week: int = None) -> List[BoxScore]:
    #     '''Returns list of box score for a given week\n
    #     Should only be used with most recent season'''
    #     if self.year < 2019:
    #         raise Exception('Cant use box score before 2019')
    #     matchup_period = self.currentMatchupPeriod
    #     scoring_period = self.current_week
    #     if week and week <= self.current_week:
    #         scoring_period = week
    #         for matchup_id in self.settings.matchup_periods:
    #             if week in self.settings.matchup_periods[matchup_id]:
    #                 matchup_period = matchup_id
    #                 break
    #
    #     params = {
    #         'view': ['mMatchupScore', 'mScoreboard'],
    #         'scoringPeriodId': scoring_period,
    #     }
    #
    #     filters = {"schedule": {"filterMatchupPeriodIds": {"value": [matchup_period]}}}
    #     headers = {'x-fantasy-filter': json.dumps(filters)}
    #     data = self.espn_request.league_get(params=params, headers=headers)
    #
    #     schedule = data['schedule']
    #     pro_schedule = self._get_pro_schedule(scoring_period)
    #     positional_rankings = self._get_positional_ratings(scoring_period)
    #     box_data = [BoxScore(matchup, pro_schedule, positional_rankings, scoring_period, self.year) for matchup in schedule]
    #
    #     for team in self.teams:
    #         for matchup in box_data:
    #             if matchup.home_team == team.team_id:
    #                 matchup.home_team = team
    #             elif matchup.away_team == team.team_id:
    #                 matchup.away_team = team
    #     return box_data

    # def power_rankings(self, week: int = None): TODO
    #     '''Return power rankings for any week'''
    #
    #     if not week or week <= 0 or week > self.current_week:
    #         week = self.current_week
    #     # calculate win for every week
    #     win_matrix = []
    #     teams_sorted = sorted(self.teams, key=lambda x: x.team_id,
    #                           reverse=False)
    #
    #     for team in teams_sorted:
    #         wins = [0] * len(teams_sorted)
    #         for mov, opponent in zip(team.mov[:week], team.schedule[:week]):
    #             opp = teams_sorted.index(opponent)
    #             if mov > 0:
    #                 wins[opp] += 1
    #         win_matrix.append(wins)
    #     dominance_matrix = two_step_dominance(win_matrix)
    #     power_rank = power_points(dominance_matrix, teams_sorted, week)
    #     return power_rank

    # def free_agents(self, week: int = None, size: int = 50, position: str = None, position_id: int = None) -> List[Player]:
    #     '''Returns a List of Free Agents for a Given Week\n
    #     Should only be used with most recent season'''
    #
    #     if self.year < 2019:
    #         raise Exception('Cant use free agents before 2019')
    #     if not week:
    #         week = self.current_week
    #
    #     slot_filter = []
    #     if position and position in POSITION_MAP:
    #         slot_filter = [POSITION_MAP[position]]
    #     if position_id:
    #         slot_filter.append(position_id)
    #
    #     params = {
    #         'view': 'kona_player_info',
    #         'scoringPeriodId': week,
    #     }
    #     filters = {"players": {"filterStatus": {"value": ["FREEAGENT", "WAIVERS"]}, "filterSlotIds": {"value": slot_filter}, "limit": size, "sortPercOwned": {"sortPriority": 1, "sortAsc": False}, "sortDraftRanks": {"sortPriority": 100, "sortAsc": True, "value": "STANDARD"}}}
    #     headers = {'x-fantasy-filter': json.dumps(filters)}
    #
    #     data = self.espn_request.league_get(params=params, headers=headers)
    #
    #     players = data['players']
    #     pro_schedule = self._get_pro_schedule(week)
    #     positional_rankings = self._get_positional_ratings(week)
    #
    #     return [BoxPlayer(player, pro_schedule, positional_rankings, week, self.year) for player in players]

    # def player_info(self, name: str = None, playerId: int = None):
    #     ''' Returns Player class if name found '''
    #
    #     if name:
    #         playerId = self.player_map.get(name)
    #     if playerId is None or isinstance(playerId, str):
    #         return None
    #     params = {'view': 'kona_playercard'}
    #     filters = {'players': {'filterIds': {'value': [playerId]}, 'filterStatsForTopScoringPeriodIds': {'value': 16, "additionalValue": ["00{}".format(self.year), "10{}".format(self.year)]}}}
    #     headers = {'x-fantasy-filter': json.dumps(filters)}
    #
    #     data = self.espn_request.league_get(params=params, headers=headers)
    #
    #     if len(data['players']) > 0:
    #         return Player(data['players'][0], self.year)
