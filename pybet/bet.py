from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MoneyLine:
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
        
    def evaluate(self, prediction):
        return prediction.win_pct / self.implied_probability - 1
        
    def __str__(self):
        return '{} ({}) MoneyLine at {}'.format(self.team.nickname, self.team.league, self.odds)

    
class Spread(MoneyLine):
    def __init__(self, team, odds, spread):
        super().__init__(team, odds)
        self.spread = spread
        
    def evaluate(self, prediction):
        if self.spread < 0:
            return prediction.spread / self.spread - 1
        else:
            return self.spread / prediction.spread - 1
    
    def __str__(self):
        return '{} ({}) against the spread ({}) at {}'.format(self.team.nickname, self.team.league, self.spread, self.odds)


class Sportsbook:
    def __init__(self, name):
        self.name = name
        self.ats_history = defaultdict(list)
        self.moneyline_history = defaultdict(list)
        
    def get_line_history(self, team, date, wager_type):
        wager_type = wager_type.lower()
        if wager_type == 'moneyline':
            return self.moneyline_history[(team, date)]
        elif wager_type in ('ats', 'spread', 'point spread', 'run line'):
            return self.ats_history[(team, date)]
        else:
            raise TypeError('Unsupported wager type: {}'.format(wager_type))
        
    def add_line(self, wager, date):
        if type(wager) == Spread:
            self.ats_history[(wager.team, date)].append(wager)
            logger.info('Added spread wager for {}: ({}) to {}'.format(wager.team.nickname, id(wager.team), self.name))
        elif type(wager) == MoneyLine:
            self.moneyline_history[(wager.team, date)].append(wager)
            logger.info('Added moneyline wager for {}: ({}) to {}'.format(wager.team.nickname, id(wager.team), self.name))
        else:
            raise TypeError('Unsupported wager type {}'.format(type(wager)))
        
    def current_line(self, team, date, wager_type):
        hist = self.get_line_history(team, date, wager_type)
        if not hist:
            return None
        return hist[-1]

        
def overround(*wagers):
    total_implied = sum(bet.implied_probability for bet in wagers)
    return total_implied - 1

