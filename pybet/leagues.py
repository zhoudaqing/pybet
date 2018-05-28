from collections import namedtuple


Team = namedtuple('Team', 'short city nickname league')

MLB_TEAMS = [
            Team('WAS', 'Washington', 'Nationals', 'mlb'),
            Team('PIT', 'Pittsburgh', 'Pirates', 'mlb'),
            Team('NYM', 'New York', 'Mets', 'mlb'),
            Team('ATL', 'Atlanta', 'Braves', 'mlb'),
            Team('LAD', 'Los Angeles', 'Dodgers', 'mlb'),
            Team('ARI', 'Arizona', 'Diamondbacks', 'mlb'),
            Team('NYY', 'New York', 'Yankees', 'mlb'),
            Team('HOU', 'Houston', 'Astros', 'mlb'),
            Team('DET', 'Detroit', 'Tigers', 'mlb'),
            Team('KAN', 'Kansas City', 'Royals', 'mlb'),
            Team('BOS', 'Boston', 'Red Sox', 'mlb'),
            Team('TEX', 'Texas', 'Rangers', 'mlb'),
            Team('CHW', 'Chicago', 'White Sox', 'mlb'),
            Team('MIN', 'Minnesota', 'Twins', 'mlb'),
            Team('LAA', 'Los Angeles', 'Angels', 'mlb'),
            Team('BAL', 'Baltimore', 'Orioles', 'mlb'),
            Team('OAK', 'Oakland', 'Athletics', 'mlb'),
            Team('SEA', 'Seattle', 'Mariners', 'mlb'),
            Team('TOR', 'Toronto', 'Blue Jays', 'mlb'),
            Team('CLE', 'Clevland', 'Indians', 'mlb'),
            Team('TAM', 'Tampa Bay', 'Rays', 'mlb'),
            Team('MIL', 'Milwaukee', 'Brewers', 'mlb'),
            Team('CHC', 'Chicago', 'Cubs', 'mlb'),
            Team('STL', 'St. Louis', 'Cardinals', 'mlb'),
            Team('COL', 'Colorado', 'Rockies', 'mlb'),
            Team('SFO', 'San Francisco', 'Giants', 'mlb'),
            Team('MIA', 'Miami', 'Marlins', 'mlb'),
            Team('PHI', 'Philadelphia', 'Phillies', 'mlb'),
            Team('CIN', 'Cincinnati', 'Reds', 'mlb'),
            Team('SDG', 'San Diego', 'Padres', 'mlb')
        ]
        
NBA_TEAMS = [
            Team('ATL', 'Atlanta', 'Hawks', 'nba'),
            Team('BKN', 'Brooklyn', 'Nets', 'nba'),
            Team('BOS', 'Boston', 'Celtics', 'nba'),
            Team('CHA', 'Charlotte', 'Hornets', 'nba'),
            Team('CHI', 'Chicago', 'Bulls', 'nba'),
            Team('CLE', 'Cleveland', 'Cavaliers', 'nba'),
            Team('DAL', 'Dallas', 'Mavericks', 'nba'),
            Team('DEN', 'Denver', 'Nuggets', 'nba'),
            Team('DET', 'Detroit', 'Pistons', 'nba'),
            Team('GSW', 'Golden State', 'Warriors', 'nba'),
            Team('HOU', 'Houston', 'Rockets', 'nba'),
            Team('IND', 'Indiana', 'Pacers', 'nba'),
            Team('LAC', 'Los Angeles', 'Clippers', 'nba'),
            Team('LAL', 'Los Angeles', 'Lakers', 'nba'),
            Team('MEM', 'Memphis', 'Grizzlies', 'nba'),
            Team('MIA', 'Miami', 'Heat', 'nba'),
            Team('MIL', 'Milwaukee', 'Bucks', 'nba'),
            Team('MIN', 'Minnesota', 'Timberwolves', 'nba'),
            Team('NOP', 'New Orleans', 'Pelicans', 'nba'),
            Team('NYK', 'New York', 'Knicks', 'nba'),
            Team('OKC', 'Oklahoma City', 'Thunder', 'nba'),
            Team('ORL', 'Orlando', 'Magic', 'nba'),
            Team('PHI', 'Philadelphia', '76ers', 'nba'),
            Team('PHX', 'Phoenix', 'Suns', 'nba'),
            Team('POR', 'Portland', 'Trail Blazers', 'nba'),
            Team('SAC', 'Sacramento', 'Kings', 'nba'),
            Team('SAS', 'San Antonio', 'Spurs', 'nba'),
            Team('TOR', 'Toronto', 'Raptors', 'nba'),
            Team('UTA', 'Utah', 'Jazz', 'nba'),
            Team('WAS', 'Washington', 'Wizards', 'nba')
            ]

def _get_teams(league):
    TEAMS = {'mlb': MLB_TEAMS,
             'nba': NBA_TEAMS}
    return TEAMS[league]


def find_team(name, league):
    teams = _get_teams(league)
    for team in teams:
        if name.lower() in [n.lower() for n in team._asdict().values()]:
            return team
    raise KeyError('Cannot find an {} team called {}'.format(league, name))
        
