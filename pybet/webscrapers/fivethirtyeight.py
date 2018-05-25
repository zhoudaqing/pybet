import datetime
import logging
import sys
import calendar
import re

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
        logger.debug('Looking for contests on {}'.format(today))
        
        model_output = []
        for away_tag, home_tag in pair_teams(team_rows):
            away = ModelTeamPrediction(away_tag)
            home = ModelTeamPrediction(home_tag, date=away.date)

            if today != away.date:
                continue
            else:
                model_output.extend((away, home))
        logger.debug('Scraped {} baseball games from FiveThirtyEight'.format(len(model_output)))
        
        if not model_output:
            sys.exit('No contests were scraped from FiveThirtyEight. Try again later')
            
        return model_output
                        
    def get_game_table(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        div = soup.find('div', {'class':'games'})
        return div.find('tbody')
        

class BasketballModel:
    def __init__(self):
        self.url = 'https://projects.fivethirtyeight.com/2018-nba-predictions/games/'
        
    def scrape_daily_teams(self):
        todays_games = self.get_todays_games()
        team_rows = [row for table in todays_games.find_all('tbody', {'class': 'ie10up'}) 
                     for row in table.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['tr'])]
        model_output = []
        for away, home in pair_teams(team_rows):
            aname = [c for c in away.find('td', {'class': 'team'}).children][0]
            hname = [c for c in home.find('td', {'class': 'team'}).children][0]
            aspread, hspread = self.parse_point_spread(away, home)
            achance = float(away.find('td', {'class': 'td number chance'}).text.strip('%'))/100
            hchance = float(home.find('td', {'class': 'td number chance'}).text.strip('%'))/100
            away = ModelTeamPrediction(team=aname, win_pct=achance, spread=aspread)
            home = ModelTeamPrediction(team=hname, win_pct=hchance, spread=hspread)
            model_output.extend((away, home))
        return model_output
    
    def get_todays_games(self):
        today = datetime.date.today()
        today = re.compile(r'{}\.? {}'.format(calendar.month_abbr[today.month], today.day))
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        day_tables = soup.find_all('section', {'class': 'day upcoming week-ahead'})
        for day in day_tables:
            if re.search(today, day.next.text):
                return day
        sys.exit('No contests were scraped from FiveThirtyEight. Try again later')
        
    @staticmethod
    def parse_point_spread(away_tag, home_tag):
        aspread = away_tag.find('td', {'class': 'td number spread'}).text
        hspread = home_tag.find('td', {'class': 'td number spread'}).text
        if aspread == 'PK' or hspread == 'PK':
            aspread = 0.0
            hspread = 0.0
        elif aspread == ' ':
            hspread = float(hspread)
            aspread = abs(hspread)
        else:
            aspread = float(aspread)
            hspread = abs(hspread)
        return aspread, hspread
        
        
class ModelTeamPrediction:
    def __init__(self, html=None, *, date=None, team=None, win_pct=None, spread=None):
        self.html = html
        self._date = date
        self._team = team
        self._win_pct = win_pct
        self._spread = spread
        
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
    
    @property
    def spread(self):
        return self._spread
            
    def __repr__(self):
        return 'FiveThirtyEight Prediction: {} - {:.0f}%'.format(self.team, self.win_pct*100)

            
def pair_teams(iterable):
    i = iter(iterable)
    return list(zip(i, i))
