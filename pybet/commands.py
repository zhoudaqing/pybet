import datetime
import logging

from pybet.webscrapers.fivethirtyeight import BaseballModel, pair_teams
from pybet.webscrapers.vegasinsider import VegasInsider
from pybet.bet import Contest


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def get_best_line(team_prediction, bookies):
	books_offering_lines = [b for b in bookies if b.current_line(team_prediction.team) is not None]
	best_book = max(books_offering_lines, key=lambda b: team_prediction.win_pct / b.current_line(team_prediction.team).implied_probability - 1)
	logger.debug('Best bookie for {} is {}'.format(team_prediction.team, best_book.name))
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
			
	
def best_bets():
	vegas = VegasInsider()
	model = BaseballModel()
	
	today = datetime.date.today()
	
	daily_predictions = model.scrape_daily_teams()
	logger.debug('Got {} team predictions from FiveThirtyEight'.format(len(daily_predictions)))
	matchups = pair_teams([prediction.team for prediction in daily_predictions])
	
	vegas.build_line_history(matchups, today)
	logger.debug('Built {} sportsbooks'.format(len(vegas.books)))
	
	lines = []
	for team_prediction in daily_predictions:
		bookie_obj, line_obj = get_best_line(team_prediction, vegas.books)
		implied = line_obj.implied_probability
		opponent = find_oppenent(team_prediction.team, matchups)
		opponent_line = bookie_obj.current_line(opponent)
		match = Contest(line_obj, opponent_line)
		lines.append((bookie_obj.name, line_obj, team_prediction.win_pct / implied - 1, match.overround))
	
	lines.sort(key=lambda w : w[2], reverse=True)
	
	for bet in lines:
		print('{} {} at {} with a value of {:.2f}% and house edge of {:.2f}%'.format(bet[0], bet[1].team, bet[1].odds, bet[2]*100, bet[3]*100))
		
		
		
			

		
	
	
		
		
			
	
	
		
	
		
	