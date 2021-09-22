import copy
import multiprocessing
import threading
import time
from queue import LifoQueue
from multiprocessing.queues import Queue, SimpleQueue
from threading import Thread

from constants import SCHEDULE
import itertools


class PlayoffPredictor():
    how_many_times = 0

    def __init__(self, slim_teams):
        self.teams = slim_teams
        # print(slim_teams)
        self.current_week = self.teams[1].wins + self.teams[1].losses + self.teams[1].ties + 1

    def get_playoff_teams(self):
        if not self.is_reg_season_over():
            raise RuntimeError("Cannot determine playoff teams before the regular season is over")

        standings = sorted(self.teams, key=lambda t: t.wins, reverse=True)
        # if team is top 6 and not tied with someone 7th or worse, then they would go to the playoffs.
        # assign 1 since they'd be a playoff team in this scenario

        # if team is top 6 and tied with someone 7th or worse, then they might go to the playoffs.
        # assign 1 / (number of teams tied for 6th)

        # if team is bottom 6 and not tied with a top 6 team, then it wouldn't make the playoffs
        # assign 0 since the team wouldn' thave made the playoffs in this scenario

    def is_reg_season_over(self):
        for team in self.teams.values():
            if (team.wins + team.ties + team.losses) < 4:
                # if (team.wins + team.ties + team.losses) != 14:
                return False
        return True

    def simulate_outcomes(self):
        """
        Simulate all of the possible outcomes as PlayoffPredictor instances, each playing out one of the possible future outcomes"""
        # 46.76; < 4
        if self.is_reg_season_over():
            # print("done, start counting values")
            PlayoffPredictor.how_many_times = PlayoffPredictor.how_many_times + 1
            print(PlayoffPredictor.how_many_times)
            # standings = sorted(self.teams.values(), key=lambda t: t.wins, reverse=True)
            # print(standings)
        else:
            matchup_tuples = []  # build a list of tuples that include the team_id's for teams playing each other
            traversed_teams = []  # keep track of teams we've recorded as being in a matchup
            for team_id in self.teams.keys():
                if team_id not in traversed_teams:
                    opponent_id = SCHEDULE[team_id][self.current_week]
                    matchup_tuples.append((team_id, opponent_id))
                    traversed_teams.append(team_id)
                    traversed_teams.append(opponent_id)

            # possible_outcomes is a list of tuples where each binary values corresponds with the winner of that matchup
            possible_outcomes = list(itertools.product([0, 1], repeat=len(matchup_tuples)))
            if len(possible_outcomes[0]) != len(matchup_tuples):
                raise RuntimeError("The predicted outcomes [{}] doesn't align with the number of matchups [{}]".format(possible_outcomes[0], len(matchup_tuples)))

            # predictors = []
            for outcome in possible_outcomes:
                teams_copy = copy.deepcopy(self.teams)
                for i, val in enumerate(outcome):
                    winner_id = matchup_tuples[i][val]
                    loser_index = 1 if val == 0 else 0
                    loser_id = matchup_tuples[i][loser_index]

                    teams_copy[winner_id].wins = teams_copy[winner_id].wins + 1
                    teams_copy[loser_id].losses = teams_copy[loser_id].losses + 1
                # predictors.append(PlayoffPredictor(teams_copy))
                PlayoffPredictor(teams_copy).simulate_outcomes()
            # return predictors


class SlimTeam():
    def __init__(self, team):
        self.id = team.id
        self.url = team.url
        self.team_name = team.team_name
        self.team_owner = team.team_owner
        self.wins = team.wins
        self.losses = team.losses
        self.ties = team.ties

    def __repr__(self):
        return 'Name: {}, id: {}, wins: {}, losses: {}, ties: {}'.format(self.team_name, self.id, self.wins, self.losses, self.ties)


class Odds():
    def __init__(self, num_teams):
        self.outcomes = 0
        self.probability_sums = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0}

    def add_prob(self, team_id, prob):
        self.probability_sums[team_id] = self.probability_sums[team_id] + prob

