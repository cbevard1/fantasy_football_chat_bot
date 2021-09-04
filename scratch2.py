from ff_bot.nfl_fantasy import League
league = League(91, debug=True)
print(league.teams)

# import re
# import requests
# from bs4 import BeautifulSoup
#
# FANTASY_NFL_ROOT_URL = 'https://fantasy.nfl.com'
# HEADERS = {"User-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
# league_id = 92
#
# standings_table = None
# fab = None
# while(standings_table is None and fab is None):
#     league_url = '{}/league/{}'.format(FANTASY_NFL_ROOT_URL, league_id)
#     page = requests.get(league_url, headers=HEADERS)
#     soup = BeautifulSoup(page.content, 'html.parser')
#
#     # get the league size
#     standings_table = soup.find(id="leagueHomeStandings")
#     fab = soup.find("td", attrs={"class": re.compile(r'^teamWaiverBudget*')})
#     print(standings_table)
#     print(fab)
#     print(league_id)
#     league_id = league_id + 1

# import time
#
#
# import asyncio
# from aiohttp import ClientSession
#
# async def fetch_player(url):
#     print("start")
#     async with ClientSession() as session:
#         async with session.get(url) as response:
#             print("await")
#             page = await response.read()
#             print("got response")
# async def run_alot():
#     for r in range(5):
#         for team in range(1, 33):
#             url = 'https://fantasy.nfl.com/players/card?leagueId=91&playerId=1000{}'.format(team)
#             await fetch_player(url)
#             print(team)
# t = time.time()
# asyncio.run(run_alot())
# print(time.time() - t)


# import aiohttp
# import asyncio
# import time
#
# start_time = time.time()
#
#
# async def main():
#     t = time.time()
#     async with aiohttp.ClientSession() as session:
#         for number in range(1, 151):
#             pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{number}'
#             print("start")
#             async with session.get(pokemon_url) as resp:
#                 print("await")
#                 pokemon = await resp.json()
#                 print(pokemon['name'])
#     print(time.time() - t)
#
# asyncio.run(main())