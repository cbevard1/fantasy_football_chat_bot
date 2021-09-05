# from .constant import POSITION_MAP, PRO_TEAM_MAP, PLAYER_STATS_MAP
# from .utils import json_parsing

import re


class Player(object):
    """Player are part of team"""

    def __init__(self, url, name, pro_team, position, benched):
        self.url = url
        self.id = self._get_player_id()
        self.name = name
        self.pos = position
        self.benched = benched
        self.season_points = None
        self.points_dict = None
        self.posRank = None
        self.pro_team = pro_team
        self.injured_status = None
        self.injured = False
        self.bye_week = None
        self.image_url = None


    def _get_player_id(self):
        query_params = self.url.split(r'?')[1]
        kv_pairs = query_params.split(r'&')
        for pair in kv_pairs:
            if(re.match(r"^playerId=\d+", pair)):
                return int(pair.split('=')[1])
        return None

    async def load_player(self, soup):
        player_card_bio = soup.find("div", attrs={"id": "playerPanel"})
        image_url = player_card_bio.find("img", attrs={"class": "player-card-bio-list-player-headshot"})["src"]
        if(self.pos != 'DEF'):
            self.injured_status = player_card_bio.find("li", attrs={"class": "player-card-bio-list-status"}).find("strong").text

        player_stat_bar = soup.find("div", attrs={"class": "player-card-stat-bar"})
        bye_week = player_stat_bar.find("em", text=re.compile("^Bye Week$")).next_sibling.text
        pos_rank = player_stat_bar.find("em", text=re.compile("^Rank$")).next_sibling.text

        mini_stats_container = soup.find("div", attrs={"class": "miniStatsContainer"})
        stat_table_rows = mini_stats_container.find("tbody").findAll("tr")
        points_dict = {}
        for row in stat_table_rows:
            week = int(row.find("td", attrs={"class": re.compile(r"^weeklyName")}).text)
            points = float(row.find("span", attrs={"class": re.compile(r"^playerTotal")}).text)
            points_dict[week] = points

        self.points_dict = points_dict
        self.bye_week = bye_week
        self.posRank = pos_rank
        self.image_url = image_url

    def fetch_points_for_week(self, week):
        if(type(week) is not int or week < 1 or week > 18):
            return 0
        return self.points_dict[week]

    def get_points_total(self):
        return sum(self.points_dict.values())

    def __repr__(self):
        return 'Player(%s)' % (self.name,)