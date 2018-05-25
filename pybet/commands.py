import datetime
import logging
import sys

from pybet.webscrapers.fivethirtyeight import BaseballModel, pair_teams
from pybet.webscrapers.vegasinsider import VegasInsider
from pybet.bet import Contest


logger = logging.getLogger(__name__)


def get_best_line(team_prediction, bookies):
    books_offering_lines = [b for b in bookies if b.current_line(team_prediction.team) is not None]
    if not books_offering_lines:
        return
    best_book = max(books_offering_lines, key=lambda b: team_prediction.win_pct / b.current_line(team_prediction.team).implied_probability - 1)
    logger.debug('{} provides the best line for {}'.format(best_book.name, team_prediction.team))
    return (best_book, best_book.current_line(team_prediction.team))
    

def find_oppenent(team, matchups):
    for pairing in matchups:
        l = list(pairing)
        if team in l:
            l.remove(team)
            opp = l[0]
            logger.debug('{}\'s opponent is {}'.format(team, opp))
            return opp
    raise RuntimeError('No opponent found for {}'.format(team))
            
    
def best_bets(league=None, sportsbooks=None):
    vegas = VegasInsider()
    model = BaseballModel()
    
    today = datetime.date.today()
    
    daily_predictions = model.scrape_daily_teams()
    matchups = pair_teams([prediction.team for prediction in daily_predictions])
    
    vegas.build_line_history(matchups, today)
    
    if sportsbooks is None:
        books = vegas.books  # if no books are specified use all of them
    else:
        books = [vegas.find_sportsbook(b) for b in sportsbooks]  # otherwise get the Sportsbook object for each name
    
    logger.debug('Looking for lines from {} sportsbooks'.format(len(books)))
        
    lines = []
    for team_prediction in daily_predictions:
        best = get_best_line(team_prediction, books)
        if not best:  # the current sportsbooks is not offering lines for the current team
            continue
        bookie_obj, line_obj = best
        implied = line_obj.implied_probability
        opponent = find_oppenent(team_prediction.team, matchups)
        opponent_line = bookie_obj.current_line(opponent)
        match = Contest(line_obj, opponent_line)
        value = team_prediction.win_pct / implied - 1
        if value > 0:
            lines.append((bookie_obj.name, line_obj, value, match.overround))
    
    lines.sort(key=lambda w : w[2], reverse=True)
    
    for bet in lines:
        print('{} {} at {} with a value of {:.2f}% and house edge of {:.2f}%'.format(bet[0], bet[1].team, bet[1].odds, bet[2]*100, bet[3]*100))
