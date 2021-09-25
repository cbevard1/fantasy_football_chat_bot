import os

FANTASY_NFL_ROOT_URL = 'https://fantasy.nfl.com'
HEADERS = {"User-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15'}

DST_ABBR_DICT = {
    'ATL': 'Falcons',
    'BUF': 'Bills',
    'CHI': 'Bears',
    'CIN': 'Bengals',
    'CLE': 'Browns',
    'DAL': 'Cowboys',
    'DEN': 'Broncos',
    'DET': 'Lions',
    'GB': 'Packers',
    'TEN': 'Titans',
    'IND': 'Colts',
    'KC': 'Chiefs',
    'OAK': 'Raiders',
    'LV': 'Raiders',
    'LAR': 'Rams',
    'LA': 'Rams',
    'MIA': 'Dolphins',
    'MIN': 'Vikings',
    'NE': 'Patriots',
    'NO': 'Saints',
    'NYG': 'Giants',
    'NYJ': 'Jets',
    'PHI': 'Eagles',
    'ARI': 'Cardinals',
    'PIT': 'Steelers',
    'LAC': 'Chargers',
    'SF': '49ers',
    'SEA': 'Seahawks',
    'TB': 'Buccaneers',
    'WSH': 'FB Team',
    'CAR': 'Panthers',
    'JAX': 'Jaguars',
    'BAL': 'Ravens',
    'HOU': 'Texans'
}

DST_ABBR_DICT = {
    'ATL': 'Falcons',
    'BUF': 'Bills',
    'CHI': 'Bears',
    'CIN': 'Bengals',
    'CLE': 'Browns',
    'DAL': 'Cowboys',
    'DEN': 'Broncos',
    'DET': 'Lions',
    'GB': 'Packers',
    'TEN': 'Titans',
    'IND': 'Colts',
    'KC': 'Chiefs',
    'OAK': 'Raiders',
    'LV': 'Raiders',
    'LAR': 'Rams',
    'LA': 'Rams',
    'MIA': 'Dolphins',
    'MIN': 'Vikings',
    'NE': 'Patriots',
    'NO': 'Saints',
    'NYG': 'Giants',
    'NYJ': 'Jets',
    'PHI': 'Eagles',
    'ARI': 'Cardinals',
    'PIT': 'Steelers',
    'LAC': 'Chargers',
    'SF': '49ers',
    'SEA': 'Seahawks',
    'TB': 'Buccaneers',
    'WSH': 'FB Team',
    'CAR': 'Panthers',
    'JAX': 'Jaguars',
    'BAL': 'Ravens',
    'HOU': 'Texans'
}

PRO_TEAM_NAMES = ['Arizona Cardinals',
                  'Atlanta Falcons',
                  'Baltimore Ravens',
                  'Buffalo Bills',
                  'Carolina Panthers',
                  'Chicago Bears',
                  'Cincinnati Bengals',
                  'Cleveland Browns',
                  'Dallas Cowboys',
                  'Denver Broncos',
                  'Detroit Lions',
                  'Green Bay Packers',
                  'Houston Texans',
                  'Indianapolis Colts',
                  'Jacksonville Jaguars',
                  'Kansas City Chiefs',
                  'Las Vegas Raiders',
                  'Los Angeles Chargers',
                  'Los Angeles Rams',
                  'Miami Dolphins',
                  'Minnesota Vikings',
                  'New England Patriots',
                  'New Orleans Saints',
                  'New York Giants',
                  'New York Jets',
                  'Philadelphia Eagles',
                  'Pittsburgh Steelers',
                  'San Francisco 49ers',
                  'Seattle Seahawks',
                  'Tampa Bay Buccaneers',
                  'Tennessee Titans',
                  'Washington Football Team']

INACTIVE_INJURY_DESIGNATIONS = ['IR', 'COV', 'O']

'''Nested dictionary that can be used to lookup games schedule. Index by team_id then week'''
SCHEDULE = {
    1: {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 12, 12: 2, 13: 3, 14: 4},
    2: {1: 1, 2: 4, 3: 6, 4: 8, 5: 10, 6: 12, 7: 3, 8: 5, 9: 7, 10: 9, 11: 11, 12: 1, 13: 4, 14: 6},
    3: {1: 12, 2: 1, 3: 5, 4: 7, 5: 9, 6: 11, 7: 2, 8: 4, 9: 6, 10: 8, 11: 10, 12: 12, 13: 1, 14: 5},
    4: {1: 11, 2: 2, 3: 1, 4: 6, 5: 8, 6: 10, 7: 12, 8: 3, 9: 5, 10: 7, 11: 9, 12: 11, 13: 2, 14: 1},
    5: {1: 10, 2: 12, 3: 3, 4: 1, 5: 7, 6: 9, 7: 11, 8: 2, 9: 4, 10: 6, 11: 8, 12: 10, 13: 12, 14: 3},
    6: {1: 9, 2: 11, 3: 2, 4: 4, 5: 1, 6: 8, 7: 10, 8: 12, 9: 3, 10: 5, 11: 7, 12: 9, 13: 11, 14: 2},
    7: {1: 8, 2: 10, 3: 12, 4: 3, 5: 5, 6: 1, 7: 9, 8: 11, 9: 2, 10: 4, 11: 6, 12: 8, 13: 10, 14: 12},
    8: {1: 7, 2: 9, 3: 11, 4: 2, 5: 4, 6: 6, 7: 1, 8: 10, 9: 12, 10: 3, 11: 5, 12: 7, 13: 9, 14: 11},
    9: {1: 6, 2: 8, 3: 10, 4: 12, 5: 3, 6: 5, 7: 7, 8: 1, 9: 11, 10: 2, 11: 4, 12: 6, 13: 8, 14: 10},
    10: {1: 5, 2: 7, 3: 9, 4: 11, 5: 2, 6: 4, 7: 6, 8: 8, 9: 1, 10: 12, 11: 3, 12: 5, 13: 7, 14: 9},
    11: {1: 4, 2: 6, 3: 8, 4: 10, 5: 12, 6: 3, 7: 5, 8: 7, 9: 9, 10: 1, 11: 2, 12: 4, 13: 6, 14: 8},
    12: {1: 3, 2: 5, 3: 7, 4: 9, 5: 11, 6: 2, 7: 4, 8: 6, 9: 8, 10: 10, 11: 1, 12: 3, 13: 5, 14: 7}
}

'''Map team ids to the manager's discord id for future features like mentioning teams in messages'''
DISCORD_ID_MAP = {
    1: None if os.getenv('TEAM1_DISCORD_ID') is None or int(os.getenv('TEAM1_DISCORD_ID')) == 0 else int(os.getenv('TEAM1_DISCORD_ID')),
    2: None if os.getenv('TEAM2_DISCORD_ID') is None or int(os.getenv('TEAM2_DISCORD_ID')) == 0 else int(os.getenv('TEAM2_DISCORD_ID')),
    3: None if os.getenv('TEAM3_DISCORD_ID') is None or int(os.getenv('TEAM3_DISCORD_ID')) == 0 else int(os.getenv('TEAM3_DISCORD_ID')),
    4: None if os.getenv('TEAM4_DISCORD_ID') is None or int(os.getenv('TEAM4_DISCORD_ID')) == 0 else int(os.getenv('TEAM4_DISCORD_ID')),
    5: None if os.getenv('TEAM5_DISCORD_ID') is None or int(os.getenv('TEAM5_DISCORD_ID')) == 0 else int(os.getenv('TEAM5_DISCORD_ID')),
    6: None if os.getenv('TEAM6_DISCORD_ID') is None or int(os.getenv('TEAM6_DISCORD_ID')) == 0 else int(os.getenv('TEAM6_DISCORD_ID')),
    7: None if os.getenv('TEAM7_DISCORD_ID') is None or int(os.getenv('TEAM7_DISCORD_ID')) == 0 else int(os.getenv('TEAM7_DISCORD_ID')),
    8: None if os.getenv('TEAM8_DISCORD_ID') is None or int(os.getenv('TEAM8_DISCORD_ID')) == 0 else int(os.getenv('TEAM8_DISCORD_ID')),
    9: None if os.getenv('TEAM9_DISCORD_ID') is None or int(os.getenv('TEAM9_DISCORD_ID')) == 0 else int(os.getenv('TEAM9_DISCORD_ID')),
    10: None if os.getenv('TEAM10_DISCORD_ID') is None or int(os.getenv('TEAM10_DISCORD_ID')) == 0 else int(os.getenv('TEAM10_DISCORD_ID')),
    11: None if os.getenv('TEAM11_DISCORD_ID') is None or int(os.getenv('TEAM11_DISCORD_ID')) == 0 else int(os.getenv('TEAM11_DISCORD_ID')),
    12: None if os.getenv('TEAM12_DISCORD_ID') is None or int(os.getenv('TEAM12_DISCORD_ID')) == 0 else int(os.getenv('TEAM12_DISCORD_ID'))
}
