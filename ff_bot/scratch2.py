import asyncio
import re

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


async def get_record():
    url = "https://fantasy.nfl.com/league/id/transactions?transactionType=add"
    async with ClientSession() as session:
        async with session.get(url) as response:
            page = await response.read()
            soup = BeautifulSoup(page, 'lxml')

            transactions_table = soup.find(id="leagueTransactions").find(lambda tag: tag.name == 'tbody')
            rows = transactions_table.findAll(lambda tag: tag.name == 'tr')
            for row in rows:
                date_str = row.find("td", attrs={"class": re.compile(r'^transactionDate*')}).text.strip()
                date_str = "{}".format(date_str)
                date = datetime.strptime(date_str, '%b %d, %I:%M%p')
                if(date.month >= 9):
                    date = date.replace(year=2021)
                else:
                    date = date.replace(year=2022)

                now = datetime.now()
                if now - timedelta(hours=24) <= date <= now:
                    team_tag = row.find("a", attrs={"class": re.compile(r'^teamName*')})
                    team_name = team_tag.text.strip()
                    team_id = team_tag['href'].split('/')[-1]
                    player_name = row.find("a", attrs={"class": re.compile(r'^playerCard playerName playerNameFull*')}).text.strip()
                    faab = row.find("td", attrs={"class": re.compile(r'^transactionTo$')}).text
                    faab = re.search("\((\d{1,}) pts\)", faab)
                    points_spent = 0
                    if(faab is not None):
                        points_spent = int(faab.group(1))
                    print("{} {} {} {} {}".format(date, team_name, player_name, points_spent, team_id))


if __name__ == '__main__':

    asyncio.run(get_record())
