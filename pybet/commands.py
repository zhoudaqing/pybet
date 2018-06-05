import datetime
import logging
import sys

from pybet.webscrapers.vegasinsider import VegasInsider
from pybet.bet import overround
from pybet.models import get_model


logger = logging.getLogger(__name__)


def find_oppenent(team, matchups):
    for matchup in matchups:
        pairing = [matchup['away'], matchup['home']]
        if team in pairing:
            pairing.remove(team)
            opp = pairing[0]
            logger.debug('{}\'s opponent is {}'.format(team.nickname, opp.nickname))
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
        matchups = [dict(away=a.team, home=h.team, start=a.date) for a,h in daily_predictions]
        vegas.build_line_history(matchups, league)
        flattened_teams = [t for p in daily_predictions for t in p]
        logger.info('Evaluating {} total {} predictions from {}'.format(len(flattened_teams), league, model))
        wagers = model.supported_wagers(league)
        logger.info('{} supports {} predictions for wager types: {}'.format(model, league, ' and '.join(wagers)))
        for team_prediction in flattened_teams:
            for wager_type in wagers:
                best = vegas.best_bet(team_prediction, wager_type, sportsbooks)
                if not best:  # no sportsbooks are offering lines for this team
                    continue
                bookie_obj, wager = best
                opponent = find_oppenent(team_prediction.team, matchups)
                opponent_line = bookie_obj.current_line(opponent, team_prediction.date, wager_type)
                juice = overround(wager, opponent_line)
                value = wager.evaluate(team_prediction)
                start = team_prediction.date.time()
                if value > 0:
                    best_bets.append((bookie_obj.name, wager, value, juice, start))
    
    best_bets.sort(key=lambda w : w[2], reverse=True)
    
    for bet in best_bets:
        time = '{}:{}'.format(bet[4].hour, str(bet[4].minute).zfill(2))
        print('{}: {} @ {} with a value of {:.2f}% and house edge of {:.2f}%'.format(bet[0], bet[1], time, bet[2]*100, bet[3]*100))
