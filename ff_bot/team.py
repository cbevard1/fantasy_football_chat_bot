import re
import sys
import traceback

from constants import HEADERS, FANTASY_NFL_ROOT_URL
from player import Player


class Team(object):
    """Teams are part of the league"""

    def __init__(self, team_id, url, name, standing, faab, pts_for, pts_against, wins, losses, ties):
        self.id = team_id
        self.url = url
        self.points_for = pts_for
        self.points_against = pts_against
        self.faab = faab
        self.team_name = name
        self.team_owner = None
        self.wins = wins
        self.losses = losses
        self.ties = ties
        self.standing = standing
        self.roster = []
        self.schedule = []
        self.streak_len = None
        self.streak_type = None

    def get_id(self):
        pattern = re.compile(r'^https://fantasy.nfl.com/league/\d+/team/(\d{1,})')
        return int(pattern.match(self.url).group(1))

    def __repr__(self):
        return 'Team(%s)' % (self.team_name,)

    async def load_team(self, soup):
        # get owner name
        team_info = soup.find("div", attrs={"class": "mod", "id": "teamDetail"})
        owner_block = team_info.find("ul", attrs={"class": "owners"})
        self.team_owner = owner_block.find("a", attrs={"class": re.compile(r'^userName*')}).text.strip()

        # get players
        # nfl.com splits players into two tables. One for offensive players, and another for DST
        # get both table bodies and combine the result set before creating a player list
        roster_table = soup.find("div", attrs={"id": "teamHome"})
        offense_table = roster_table.find("div", attrs={"id": "tableWrap-O"}).find("table").find("tbody")
        defense_table = roster_table.find("div", attrs={"id": "tableWrap-DT"}).find("table").find("tbody")
        rows = offense_table.findAll("tr", attrs={"class": re.compile(r"^player-\d")}) + defense_table.findAll("tr", attrs={"class": re.compile(r"^player-\d")})

        # tasks = []
        for row in rows:
            try:
                txt = row.text
                if (re.search("--empty--", txt)):
                    continue  # for an empty roster spot just continue to the next row
                else:
                    player_benched = False
                    if row.find("td", attrs={"class": "teamPosition first"}).text == "BN":
                        player_benched = True
                    # there might be an error here with a missing '/' between the root url and the player card url
                    player_tag = row.find("a", attrs={"class": re.compile("^playerCard*")})
                    player_url = "{}{}".format(FANTASY_NFL_ROOT_URL, player_tag["href"])
                    player_name = player_tag.text
                    pos_team_arr = player_tag.findNext("em").text.split("-")
                    position = pos_team_arr[0].strip()
                    if (len(pos_team_arr) == 2):
                        team = pos_team_arr[1].strip()
                    elif (position == "DEF"):
                        team = None  # TODO lookup city abbr from name
                    else:
                        team = "Free Agent"
                    player = Player(player_url, player_name, team, position, player_benched)
                    self.roster.append(player)
            except TypeError:
                traceback.print_exc(file=sys.stdout)
                continue

    def _fetch_roster(self, data, year):
        '''Fetch teams roster'''
        self.roster.clear()
        roster = data['entries']

        for player in roster:
            self.roster.append(Player(player, year))

    def _fetch_schedule(self, data):
        '''Fetch schedule and scores for team'''

        for matchup in data:
            if 'away' in matchup.keys():
                if matchup['away']['teamId'] == self.team_id:
                    score = matchup['away']['totalPoints']
                    opponentId = matchup['home']['teamId']
                    self.outcomes.append(matchup['winner'])
                    self.scores.append(score)
                    self.schedule.append(opponentId)
                elif matchup['home']['teamId'] == self.team_id:
                    score = matchup['home']['totalPoints']
                    opponentId = matchup['away']['teamId']
                    self.outcomes.append(matchup['winner'])
                    self.scores.append(score)
                    self.schedule.append(opponentId)
            elif matchup['home']['teamId'] == self.team_id:
                score = matchup['home']['totalPoints']
                opponentId = matchup['home']['teamId']
                self.outcomes.append(matchup['winner'])
                self.scores.append(score)
                self.schedule.append(opponentId)

    def abbr_team_name(self, num_chars):
        return (self.team_name[:num_chars].strip() + '.') if len(self.team_name) > num_chars else self.team_name
