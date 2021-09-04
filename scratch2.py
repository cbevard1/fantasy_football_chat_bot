from ff_bot.nfl_fantasy import League
league = League(91, debug=True)
print(league.teams)

import re
import requests
from bs4 import BeautifulSoup
from aiohttp import ClientSession
#
FANTASY_NFL_ROOT_URL = 'https://fantasy.nfl.com'
HEADERS = {"User-agent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
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

####### get matchup URLs

# league_url = 'https://fantasy.nfl.com/league/614261'
# page = requests.get(league_url, headers=HEADERS)
# soup = BeautifulSoup(page.content, 'lxml')
# scoring_strip = soup.find("div", attrs={"id": "leagueHomeScoreStrip"})
# # current_week = scoring_strip\
# #     .find("ul", attrs={"class": re.compile(r"^weekNav")})\
# #     .find("li", attrs={"href": None}).text\
# #     .split(" ")[1]
# matchups = scoring_strip\
#     .find("div", attrs={"class": "teamNav"})\
#     .find_all("a")
#
# hrefs = []
# for matchup in matchups:
#     hrefs.append("{}{}".format(FANTASY_NFL_ROOT_URL, matchup['href']))
#
# print(hrefs)

# url = 'https://fantasy.nfl.com/league/91/team/6'
# page = requests.get(url, headers=HEADERS)
# soup = BeautifulSoup(page.content, 'lxml')
#
# roster_table = soup.find("div", attrs={"id": "teamHome"})
# offense_table = roster_table.find("div", attrs={"id": "tableWrap-O"}).find("table").find("tbody")
# defense_table = roster_table.find("div", attrs={"id": "tableWrap-DT"}).find("table").find("tbody")
# rows = offense_table.findAll("tr", attrs={"class": re.compile(r"^player-\d")}) + defense_table.findAll("tr", attrs={"class": re.compile(r"^player-\d")})
# for row in rows:
#     if row.find("td", attrs={"class": "teamPosition first"}).text == "BN":
#         print("benched player: {}".format(row.text))

######### parse matchup
# matchup_url = 'https://fantasy.nfl.com/league/91/team/3/gamecenter?week=1'
#
# page = requests.get(matchup_url, headers=HEADERS)
# soup = BeautifulSoup(page.content, 'lxml')
#
# matchup_nav = soup.find("div", attrs={"class": "teamNav ft"})\
#     .find("li", attrs={"class": re.compile(r"^selected")})\
#     .find_all("span")
# teams = []
# for matchup in matchup_nav:
#     teams.append(matchup['class'][1].split('-')[-1])
# team_a_id = teams[0]
# team_b_id = teams[1]
#
# time_remaining_footer = soup.find("div", attrs={"id": "teamMatchupChart"}).find("div", attrs={"class": "ft"})
# print("teamMinutesRemaining minType-remaining teamId-{}".format(team_a_id))
# team1_time_remaining = int(time_remaining_footer.find("span", attrs={"class": "teamMinutesRemaining minType-remaining teamId-{}".format(team_a_id)}).text)
# team1_time_total = int(time_remaining_footer.find("span", attrs={"class": "teamMinutesRemaining minType-total teamId-{}".format(team_a_id)}).text)
# team2_time_remaining = int(time_remaining_footer.find("span", attrs={"class": "teamMinutesRemaining minType-remaining teamId-{}".format(team_b_id)}).text)
# team2_time_total = int(time_remaining_footer.find("span", attrs={"class": "teamMinutesRemaining minType-total teamId-{}".format(team_b_id)}).text)
#
# header = soup.find("div", attrs={"id": "teamMatchupHeader"})
# team1_id = int(header.find("a", attrs={"class": "teamName teamId-{}".format(team_a_id)})['href'].split('/')[-1])
# team2_id = int(header.find("a", attrs={"class": "teamName teamId-{}".format(team_b_id)})['href'].split('/')[-1])
#
# matchup_details = soup.find("div", attrs={"id": "teamMatchupSecondary"})
# team1_pts = float(matchup_details.find("span", attrs={"class": "teamTotal teamId-{}".format(team_a_id)}).text)
# team2_pts = float(matchup_details.find("span", attrs={"class": "teamTotal teamId-{}".format(team_b_id)}).text)
# team1_proj_pts = float(matchup_details.find("span", attrs={"class": "teamTotalProjected teamId-{}".format(team_a_id)}).text)
# team2_proj_pts = float(matchup_details.find("span", attrs={"class": "teamTotalProjected teamId-{}".format(team_b_id)}).text)
# team1_bench_pts = float(matchup_details.find("span", attrs={"class": "teamBenchTotal teamId-{}".format(team_a_id)}).text)
# team2_bench_pts = float(matchup_details.find("span", attrs={"class": "teamBenchTotal teamId-{}".format(team_b_id)}).text)
# team1_bench_proj_pts = float(matchup_details.find("span", attrs={"class": "teamTotalProjected teamTotalProjectedBN teamId-{}".format(team_a_id)}).text)
# team2_bench_proj_pts = float(matchup_details.find("span", attrs={"class": "teamTotalProjected teamTotalProjectedBN teamId-{}".format(team_b_id)}).text)
#
# print("{}, {}, {}, {}, {}, {}, {}".format(team1_id, team1_pts, team1_proj_pts, team1_bench_pts, team1_bench_proj_pts, team1_time_remaining, team1_time_total))
# print("{}, {}, {}, {}, {}, {}, {}".format(team2_id, team2_pts, team2_proj_pts, team2_bench_pts, team2_bench_proj_pts, team2_time_remaining, team2_time_total))
