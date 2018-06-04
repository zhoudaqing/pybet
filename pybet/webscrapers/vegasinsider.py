import re
import logging
from difflib import SequenceMatcher
import datetime

import requests
from bs4 import BeautifulSoup

from ..bet import Sportsbook, MoneyLine, Spread
from pybet.leagues import find_team


logger = logging.getLogger(__name__)

class VegasInsider:
    def __init__(self):
        self.bases = ['http://www.vegasinsider.com/{}/odds/las-vegas/line-movement',
                      'http://www.vegasinsider.com/{}/odds/offshore/line-movement']
        self.books = []
        self.league = None
        
    def build_line_history(self, matchups, league):
        self.league = league
        date = datetime.date.today()
        day = str(date.day).zfill(2)
        month = str(date.month).zfill(2)
        year = str(date.year)[-2:]
        
        for page in self.bases:
            page = page.format(league)
            for matchup in matchups:
                away = matchup['away'].nickname.replace(' ', '-')
                home = matchup['home'].nickname.replace(' ', '-')
                time = matchup['start'].time()
                site = '/{}-@-{}.cfm/date/{}-{}-{}/time/{}{}'.format(away, home, month, day, year, time.hour, str(time.minute).zfill(2))
        
                logger.info('Retrieving line history for {} @ {}'.format(matchup['away'].nickname, matchup['home'].nickname))
                r = requests.get(page + site)
                soup = BeautifulSoup(r.text, 'html.parser')
        
                bookie_tables = soup.find('div', {'SLTables1'}).find_all('table', recursive=False)[2:]
        
                for bookie in bookie_tables:
                    name = bookie.find('tr', {'class':'component_head'}).text
                    name = clean_name(name)
                    if name == 'VI CONSENSUS':
                        continue  # this is not an actual sportsbook
            
                    try:
                        sportsbook = self.find_sportsbook(name)
                    except KeyError:
                        sportsbook = Sportsbook(name)
                        self.books.append(sportsbook)
                        logger.info('Added {}'.format(name))
                
                    rows = bookie.find('table', {'class':'rt_railbox_border2'}).find_all('tr')[2:]
                    self._scrape_moneylines(rows, sportsbook)
                    self._scrape_spreads(rows, sportsbook)
            
    def find_sportsbook(self, name):
        for book in self.books:
            if name.lower() == book.name.lower():
                return book
        best_matches = self._get_best_matches(name)
        if not best_matches:
            msg = 'Could not find a sportsbooks with the name {}'.format(name)
        else:
            joined = ' or '.join(best_matches)
            msg = 'Could not find a sportsbook with the name {}. Did you mean {}?'.format(name, joined)
        raise KeyError(msg)
                          
    def _scrape_moneylines(self, html_table, sportsbook):
        for row in html_table:
            for t in row.find_all('td')[2:4]:
                t = clean_name(t.text)
                parsed = self._parse_name_and_odds(t)
                if not parsed:
                    continue
                team, odds = parsed
                sportsbook.add_line(MoneyLine(team, odds))
                
    def _scrape_spreads(self, html_table, sportsbook):
        for row in html_table:
            for t in row.find_all('td')[4:6]:
                ''' TODO: FIGURE OUT CLEANER WAY TO HANDLE MLB RUNLINES '''
                t = clean_name(t.text)
                if not t:
                    continue
                if self.league == 'mlb':
                    ats = self._parse_runline(t)
                    if not ats:
                        continue
                    sportsbook.add_line(ats)
                else:    
                    s = t.split(' ')
                    team = s[0][:3]
                    team = find_team(team, self.league)
                    try:
                        odds = int(s[1])
                    except Exception as e:
                        logger.info('Skipping {} because {}'.format(t, e))
                        continue
                    spread = float(s[0][3:])
                    sportsbook.add_line(Spread(team, odds, spread))
                
    def _parse_name_and_odds(self, table_data):
        sign_pos = re.search(r'\+|-', table_data)
        if sign_pos is None:
            return
        sign_pos = sign_pos.start()
        odds = int(table_data[sign_pos:])
        team = table_data[:sign_pos]
        team = find_team(team, self.league)
        return team, odds
        
    def _parse_runline(self, table_data):
        parsed = self._parse_name_and_odds(table_data)
        if not parsed:
            return
        team, odds = parsed
        if odds < 0:
            spread = -1.5
        else:
            spread = 1.5
        return Spread(team, odds, spread)
            
    def _get_best_matches(self, name):
        matches = []
        for book in self.books:
            ratio = SequenceMatcher(None, book.name.lower(), name.lower()).ratio()
            if ratio > .80:
                matches.append(book.name)
        return matches
            
            
def clean_name(name):
    return name.replace('\t', '').replace('\n', '').replace('\r', '').replace(' LINE MOVEMENTS', '')
