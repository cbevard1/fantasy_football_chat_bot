import re
from tabulate import tabulate

class Opponent(object):
    def __init__(self, team, score, projected_score, bench_score, bench_projected_score, min_remaining, min_total):
        self.team = team
        self.team_id = id
        self.score = score
        self.projected_score = projected_score
        self.bench_score = bench_score
        self.bench_projected_score = bench_projected_score
        self.min_remaining = min_remaining
        self.min_total = min_total


class Matchup(object):
    def __init__(self, url):
        self.url = url
        self.opp1 = None
        self.opp2 = None

    def __repr__(self):
        return '[%s] vs [%s]' % (self.opp1.team.team_name, self.opp2.team.team_name,)

    async def load_matchup(self, soup, teams):
        matchup_nav = soup.find("div", attrs={"class": "teamNav ft"}) \
            .find("li", attrs={"class": re.compile(r"^selected")}) \
            .find_all("span")
        teams_ids = []
        for matchup in matchup_nav:
            teams_ids.append(matchup['class'][1].split('-')[-1])
        team_a_id = teams_ids[0]
        team_b_id = teams_ids[1]

        time_remaining_footer = soup.find("div", attrs={"id": "teamMatchupChart"}).find("div", attrs={"class": "ft"})
        team1_time_remaining = int(time_remaining_footer.find("span", attrs={"class": "teamMinutesRemaining minType-remaining teamId-{}".format(team_a_id)}).text)
        team1_time_total = int(time_remaining_footer.find("span", attrs={"class": "teamMinutesRemaining minType-total teamId-{}".format(team_a_id)}).text)
        team2_time_remaining = int(time_remaining_footer.find("span", attrs={"class": "teamMinutesRemaining minType-remaining teamId-{}".format(team_b_id)}).text)
        team2_time_total = int(time_remaining_footer.find("span", attrs={"class": "teamMinutesRemaining minType-total teamId-{}".format(team_b_id)}).text)

        header = soup.find("div", attrs={"id": "teamMatchupHeader"})
        team1_id = int(header.find("a", attrs={"class": "teamName teamId-{}".format(team_a_id)})['href'].split('/')[-1])
        team2_id = int(header.find("a", attrs={"class": "teamName teamId-{}".format(team_b_id)})['href'].split('/')[-1])

        matchup_details = soup.find("div", attrs={"id": "teamMatchupSecondary"})
        team1_pts = float(matchup_details.find("span", attrs={"class": "teamTotal teamId-{}".format(team_a_id)}).text)
        team2_pts = float(matchup_details.find("span", attrs={"class": "teamTotal teamId-{}".format(team_b_id)}).text)
        team1_proj_pts = float(matchup_details.find("span", attrs={"class": "teamTotalProjected teamId-{}".format(team_a_id)}).text)
        team2_proj_pts = float(matchup_details.find("span", attrs={"class": "teamTotalProjected teamId-{}".format(team_b_id)}).text)
        team1_bench_pts = float(matchup_details.find("span", attrs={"class": "teamBenchTotal teamId-{}".format(team_a_id)}).text)
        team2_bench_pts = float(matchup_details.find("span", attrs={"class": "teamBenchTotal teamId-{}".format(team_b_id)}).text)
        team1_bench_proj_pts = float(matchup_details.find("span", attrs={"class": "teamTotalProjected teamTotalProjectedBN teamId-{}".format(team_a_id)}).text)
        team2_bench_proj_pts = float(matchup_details.find("span", attrs={"class": "teamTotalProjected teamTotalProjectedBN teamId-{}".format(team_b_id)}).text)

        self.opp1 = Opponent(teams[team1_id], team1_pts, team1_proj_pts, team1_bench_pts, team1_bench_proj_pts, team1_time_remaining, team1_time_total)
        self.opp2 = Opponent(teams[team2_id], team2_pts, team2_proj_pts, team2_bench_pts, team2_bench_proj_pts, team2_time_remaining, team2_time_total)

    def box_score(self):
        header = ["Team", "Projected Score", "Score"]
        score1 = [self.opp1.team.team_name.ljust(25), self.opp1.projected_score, self.opp1.score]
        score2 = [self.opp2.team.team_name.ljust(25), self.opp2.projected_score, self.opp2.score]
        return tabulate([[score1, score2], [score1, score2]], headers=header)
