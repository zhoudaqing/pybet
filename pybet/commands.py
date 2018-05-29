import datetime
import logging
import sys

from pybet.webscrapers.vegasinsider import VegasInsider
from pybet.bet import overround
from pybet.models import get_model


logger = logging.getLogger(__name__)


def get_best_line(team_prediction, bookies, wager_type):
    books_offering_lines = [b for b in bookies if b.current_line(team_prediction.team, wager_type) is not None]
    logger.info('{} sportsbooks are offering {} wagers for {}'.format(len(books_offering_lines), wager_type, team_prediction.team.nickname))
    if not books_offering_lines:
        return
    best_book = max(books_offering_lines, key=lambda b: b.current_line(team_prediction.team, wager_type).evaluate(team_prediction))
    logger.info('{} provides the best line for {}'.format(best_book.name, team_prediction.team.nickname))
    return (best_book, best_book.current_line(team_prediction.team, wager_type))
    

def find_oppenent(team, matchups):
    for pairing in matchups:
        l = list(pairing)
        if team in l:
            l.remove(team)
            opp = l[0]
            logger.info('{}\'s opponent is {}'.format(team, opp))
            return opp
    raise RuntimeError('No opponent found for {}'.format(team))
            
    
def best_bets(leagues=None, sportsbooks=None, model='FiveThirtyEight', wager=None):
    vegas = VegasInsider()
    model = get_model(model)
    
    if not leagues:
        leagues = ['mlb', 'nba']

    best_bets = []
    for league in leagues:
        daily_predictions = model.get_todays_predictions(league)
        if not daily_predictions:
            logger.info('No {} contests were scraped from {}'.format(league, model.name))
            continue
        matchups = [(a.team, h.team) for a,h in daily_predictions]
        vegas.build_line_history(matchups, league)
    
        if sportsbooks is None:
            books = vegas.books  # if no books are specified use all of them
        else:
            books = [vegas.find_sportsbook(b) for b in sportsbooks]  # otherwise get the Sportsbook object for each name
    
        logger.info('Looking for lines from {} sportsbooks'.format(len(books)))
        
        flattened_teams = [t for p in daily_predictions for t in p]
        logger.info('Evaluating {} total {} predictions from {}'.format(len(flattened_teams), league, model))
        wagers = model.supported_wagers(league)
        logger.info('{} supports {} predictions for wager types: {}'.format(model, league, ' and '.join(wagers)))
        for team_prediction in flattened_teams:
            for wager_type in wagers:
                best = get_best_line(team_prediction, books, wager_type)
                if not best:  # the current sportsbooks is not offering lines for the current team
                    continue
                bookie_obj, wager = best
                opponent = find_oppenent(team_prediction.team, matchups)
                opponent_line = bookie_obj.current_line(opponent, wager_type)
                juice = overround(wager, opponent_line)
                value = wager.evaluate(team_prediction)
                if value > 0:
                    best_bets.append((bookie_obj.name, wager, value, juice))
    
    best_bets.sort(key=lambda w : w[2], reverse=True)
    
    for bet in best_bets:
        print('{}: {} with a value of {:.2f}% and house edge of {:.2f}%'.format(bet[0], bet[1], bet[2]*100, bet[3]*100))
