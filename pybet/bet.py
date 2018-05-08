from collections import defaultdict

from .leagues.mlb import TEAMS

class Line:
	def __init__(self, team, odds):
		self.team = team
		if odds == 'EVEN':
			self.odds = 100
		else:
			self.odds = odds
		
	@property
	def implied_probability(self):	
		if self.odds < 0:
			prob = abs(self.odds)/(abs(self.odds)+100)
		else:
			prob = 100/(self.odds+100)
		return prob
		
	def __repr__(self):
		return 'Line: {} at {}'.format(self.team, self.odds)
		
		
class Contest:
	def __init__(self, *lines):
		self.lines = lines
	
	@property
	def overround(self):
		total_implied = sum(l.implied_probability for l in self.lines)
		return total_implied - 1

	@property
	def underdog(self):
		if all(self.lines[0].odds == l.odds for l in self.lines):
			return None
		favorite = max((l for l in self.lines), key=lambda l : l.odds)
		return favorite.team
		
	@property
	def favorite(self):
		if all(self.lines[0].odds == l.odds for l in self.lines):
			return None
		dog = min((l for l in self.lines), key=lambda l : l.odds)
		return dog.team

		
class Sportsbook:
	def __init__(self, name):
		self.name = name
		self.line_history = defaultdict(list)
		
	def get_line_history(self, team):
		name = normalize_name(team)
		return self.line_history[name]
		
	def add_line(self, line):
		name = normalize_name(line.team)
		self.line_history[name].append(line)
		
	def current_line(self, team):
		hist = self.get_line_history(team)
		if not hist:
			return None
		return hist[-1]
	
	
def normalize_name(name):
	for team in TEAMS:
		if name in team:
			return team[0]
		