import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from player import Player
import threading
import concurrent.futures
from multiprocessing import Pool

p = Pool(10)

class WebScraper(object):
    @staticmethod
    async def fetch_players(players):
        async with ClientSession() as session:
            for player in players:
                async with session.get(player.url) as response:
                    page = await response.read()
                    soup = BeautifulSoup(page, 'lxml')
                    await player.load_player(soup)

    @staticmethod
    async def fetch_team(teams):
        async with ClientSession() as session:
            for team in teams:
                async with session.get(team.url) as response:
                    page = await response.read()
                    soup = BeautifulSoup(page, 'lxml')
                    await team.load_team(soup)

    @staticmethod
    async def fetch_matchups(matchups, teams):
        async with ClientSession() as session:
            for matchup in matchups:
                async with session.get(matchup.url) as response:
                    page = await response.read()
                    soup = BeautifulSoup(page, 'lxml')
                    await matchup.load_matchup(soup, teams)