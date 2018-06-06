import datetime
import logging
import sys
import calendar
import re
import datetime

import requests
from bs4 import BeautifulSoup
from dateutil import parser

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
        aname = atag.find('span', {'class': 'team-name long'}).text
        dt_str = atag.find('span', {'class':'day long'}).text
        dt = parser.parse(dt_str).date()
        tm_str = atag.find('span', {'class': 'time'}).text
        i = tm_str.find('.m.')
        tm_str = tm_str[:i+3]  # remove timezone text if present
        tm = parser.parse(tm_str).time()
        dtime = datetime.datetime.combine(dt, tm)
        ateam = pybet.leagues.find_team(aname, 'mlb')
        win_pct = atag.find('td', {'class':'td number td-number win-prob'}).text
        win_pct = float(win_pct.strip('%'))/100
        
        if today != dt:
            return

        away = ModelTeamPrediction(date=dtime, team=ateam, win_pct=win_pct)
        
        hname = htag.find('span', {'class': 'team-name long'}).text
        hteam = pybet.leagues.find_team(hname, 'mlb')
        win_pct = htag.find('td', {'class':'td number td-number win-prob'}).text
        win_pct = float(win_pct.strip('%'))/100
        home = ModelTeamPrediction(date=dtime, team=hteam, win_pct=win_pct)
        return away, home


class BasketballScraper:
    def __init__(self):
        self.url = 'https://projects.fivethirtyeight.com/2018-nba-predictions/games/'
        
    def scrape_todays_games(self):
        todays_games = self._get_todays_games()
        if not todays_games:
            return
        
        model_output = []
        today = datetime.date.today()
        for game in todays_games:
            team_rows = [row for table in game.find_all('tbody', {'class': 'ie10up'}) 
                         for row in table.find_all(lambda tag: tag.name == 'tr' and tag.get('class') == ['tr'])]  # avoids classes like "tr buffer"
            game_time = game.find('span', {'class':'desk'}).next.next
            game_time = parser.parse(game_time).time()
            for away, home in pair_teams(team_rows):
                dtime = datetime.datetime.combine(today, game_time)
                aname = [c for c in away.find('td', {'class': 'team'}).children][0]
                hname = [c for c in home.find('td', {'class': 'team'}).children][0]
                ateam = pybet.leagues.find_team(aname, 'nba')
                hteam = pybet.leagues.find_team(hname, 'nba')
                aspread, hspread = self._parse_point_spread(away, home)
                achance = float(away.find('td', {'class': 'td number chance'}).text.strip('%'))/100
                hchance = float(home.find('td', {'class': 'td number chance'}).text.strip('%'))/100
                away = ModelTeamPrediction(team=ateam, win_pct=achance, spread=aspread, date=dtime)
                home = ModelTeamPrediction(team=hteam, win_pct=hchance, spread=hspread, date=dtime)
                model_output.append((away, home))
        logger.info('Scraped {} basketball games from FiveThirtyEight'.format(len(model_output)))
        return model_output
    
    def _get_todays_games(self):
        today = datetime.date.today()
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        day_tables = soup.find_all('section', {'class': 'day upcoming week-ahead'})
        for day in day_tables:
            date_tag = day.find('h3')
            for child in date_tag.find_all('span'):
                child.decompose()
            if parser.parse(date_tag.text).date() == today:
                return day.find_all('table', {'class': 'pre'})
        
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
            hspread = abs(aspread)
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
