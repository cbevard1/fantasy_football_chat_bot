# from .constant import POSITION_MAP, PRO_TEAM_MAP, PLAYER_STATS_MAP
# from .utils import json_parsing
import requests
import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from .constants import HEADERS, FANTASY_NFL_ROOT_URL
import re


class Player(object):
    """Player are part of team"""

    def __init__(self, url, name, pro_team, position):
        self.url = url
        self.name = name
        self.pos = position
        self.season_points = None
        self.points_dict = None
        self.posRank = None
        self.pro_team = pro_team
        self.injured_status = None
        self.injured = False
        self.bye_week = None
        self.image_url = None

    async def _fetch_player(self):
        print("started player...")
        async with ClientSession() as session:
            async with session.get(self.url) as response:
                page = await response.read()
                print("got response")
                soup = BeautifulSoup(page, 'html.parser')

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
                print("finished player")

    def load_player(self, soup):
        print("started player...")
        # async with ClientSession() as session:
        #     async with session.get(self.url) as response:
        #         page = await response.read()
        #         print("got response")
        #         soup = BeautifulSoup(page, 'html.parser')

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
        print("finished player")

    def _fetch_points_for_week(self, week):
        if(type(week) is not int or week < 1 or week > 18):
            return 0
        return self.points_dict[week]

    def __repr__(self):
        return 'Player(%s)' % (self.name,)