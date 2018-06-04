import datetime
import logging
import sys
import calendar
import re

import requests
from bs4 import BeautifulSoup

import pybet.leagues


logger = logging.getLogger(__name__)


class BaseballScraper:
    def __init__(self):
        self.url = 'https://projects.fivethirtyeight.com/2018-mlb-predictions/games/'
        
    def scrape_todays_games(self):
        game_table = self._get_game_table()
        team_rows = game_table.find_all('tr')
        
        model_output = []
        for away_tag, home_tag in pair_teams(team_rows):
            preds = self._parse_team_predictions(away_tag, home_tag)
            if not preds:
                continue
            else:
                model_output.append(preds)
            
        logger.info('Scraped {} baseball games from FiveThirtyEight'.format(len(model_output)))            
        return model_output
                        
    def _get_game_table(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        div = soup.find('div', {'class':'games'})
        return div.find('tbody')
    
    @staticmethod
    def _parse_team_predictions(atag, htag):
        ''' parse away team first since the date from this HTML tag will be needed
        with the home team prediction '''
        today = datetime.date.today()
        today = '{}/{}'.format(today.month, today.day)
        
        aname = atag.find('span', {'class': 'team-name long'}).text
        dt = atag.find('span', {'class':'day short'}).text
        ateam = pybet.leagues.find_team(aname, 'mlb')
        win_pct = atag.find('td', {'class':'td number td-number win-prob'}).text
        win_pct = float(win_pct.strip('%'))/100
        away = ModelTeamPrediction(date=dt, team=ateam, win_pct=win_pct)
        
        if today != dt:
            return
        
        hname = htag.find('span', {'class': 'team-name long'}).text
        hteam = pybet.leagues.find_team(hname, 'mlb')
        win_pct = htag.find('td', {'class':'td number td-number win-prob'}).text
        win_pct = float(win_pct.strip('%'))/100
        home = ModelTeamPrediction(date=dt, team=hteam, win_pct=win_pct)
        return away, home


class BasketballScraper:
    def __init__(self):
        self.url = 'https://projects.fivethirtyeight.com/2018-nba-predictions/games/'
        
    def scrape_todays_games(self):
        todays_games = self._get_todays_games()
        if not todays_games:
            return
        team_rows = [row for table in todays_games.find_all('tbody', {'class': 'ie10up'}) 
                     for row in table.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['tr'])]
        model_output = []
        for away, home in pair_teams(team_rows):
            aname = [c for c in away.find('td', {'class': 'team'}).children][0]
            hname = [c for c in home.find('td', {'class': 'team'}).children][0]
            ateam = pybet.leagues.find_team(aname, 'nba')
            hteam = pybet.leagues.find_team(hname, 'nba')
            aspread, hspread = self._parse_point_spread(away, home)
            achance = float(away.find('td', {'class': 'td number chance'}).text.strip('%'))/100
            hchance = float(home.find('td', {'class': 'td number chance'}).text.strip('%'))/100
            away = ModelTeamPrediction(team=ateam, win_pct=achance, spread=aspread)
            home = ModelTeamPrediction(team=hteam, win_pct=hchance, spread=hspread)
            model_output.append((away, home))
        logger.info('Scraped {} basketball games from FiveThirtyEight'.format(len(model_output)))
        return model_output
    
    def _get_todays_games(self):
        today = datetime.date.today()
        today = re.compile(r'{}|{}\.? {}'.format(calendar.month_abbr[today.month], today.month, today.day))  # match October or just Oct.
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        day_tables = soup.find_all('section', {'class': 'day upcoming week-ahead'})
        for day in day_tables:
            if re.search(today, day.next.text):
                return day
        
    @staticmethod
    def _parse_point_spread(away_tag, home_tag):
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
    def __init__(self, team, win_pct, spread=None, date=None):
        self._date = date
        self._team = team
        self._win_pct = win_pct
        self._spread = spread
        
    @property
    def date(self):
        return self._date

    @property
    def team(self):
        return self._team
    
    @property
    def win_pct(self):
        return round(self._win_pct, 4)
    
    @property
    def spread(self):
        return self._spread
            
    def __repr__(self):
        return 'FiveThirtyEight Prediction: {} - {:.0f}%'.format(self.team.nickname, self.win_pct*100)

            
def pair_teams(iterable):
    i = iter(iterable)
    return list(zip(i, i))
