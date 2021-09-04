import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from .player import Player
import threading
import concurrent.futures
from multiprocessing import Pool

p = Pool(10)

class WebScraper(object):
    @staticmethod
    async def fetch(players):
        async with ClientSession() as session:
            for player in players:
                async with session.get(player.url) as response:
                    page = await response.read()
                    print("got response")
                    soup = BeautifulSoup(page, 'lxml')
                    player.load_player(soup)


class WebScraper2(object):
    @staticmethod
    async def fetch(players):
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            async with ClientSession() as session:
                for player in players:
                    async with session.get(player.url) as response:
                        page = await response.read()
                        print("got response")
                        soup = BeautifulSoup(page, 'html.parser')
                        futures.append(executor.submit(player.load_player, soup))
            executor.shutdown(wait=True)
