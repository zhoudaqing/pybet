import datetime
import logging

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)

class BaseballModel:
	def __init__(self):
		self.url = 'https://projects.fivethirtyeight.com/2018-mlb-predictions/games/'
		
	def scrape_daily_teams(self):
		game_table = self.get_game_table()
		team_rows = game_table.find_all('tr')
		today = datetime.date.today()
		today = '{}/{}'.format(today.month, today.day)
		
		model_output = []
		for away_tag, home_tag in pair_teams(team_rows):
			away = ModelTeamPrediction(away_tag)
			home = ModelTeamPrediction(home_tag, date=away.date)

			if today != away.date:
				break
			else:
				model_output.extend((away, home))
		logger.debug('Scraped {} baseball games from FiveThirtyEight'.format(len(model_output)))
		return model_output
						
	def get_game_table(self):
		r = requests.get(self.url)
		soup = BeautifulSoup(r.text, 'html.parser')
		div = soup.find('div', {'class':'games'})
		return div.find('tbody')
		
		
class ModelTeamPrediction:
	def __init__(self, html=None, *, date=None, team=None, win_pct=None):
		self.html = html
		self._date = date
		self._team = team
		self._win_pct = win_pct
		
	@property
	def date(self):
		if self._date:
			return self._date
		elif self.html:
			return self.html.find('span', {'class':'day short'}).text

	@property
	def team(self):
		if self._team:
			return self._team
		elif self.html:
			return self.html.find('span', {'class':'team-name long'}).text
	
	@property
	def win_pct(self):
		if self._win_pct:
			return self._win_pct
		elif self.html:
			prob = self.html.find('td', {'class':'td number td-number win-prob'}).text
			return round(float(prob.strip('%'))/100, 4)
			
	def __repr__(self):
		return 'FiveThirtyEight Prediction: {} - {:.0f}%'.format(self.team, self.win_pct*100)

			
def pair_teams(iterable):
	i = iter(iterable)
	return list(zip(i, i))
	
	