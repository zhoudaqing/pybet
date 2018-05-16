import argparse
import logging

import pybet.commands as cmd


def setup_logging():
	root = logging.getLogger()
	root.setLevel(logging.DEBUG)
	handler = logging.StreamHandler()
	formatter = logging.Formatter(fmt='%(levelname)s_%(name)s: %(message)s')
	handler.setFormatter(formatter)
	root.addHandler(handler)
	
	
def main():
	top_parser = argparse.ArgumentParser(prog='pybet')	
	top_parser.add_argument('-v', '--verbose', action='store_true', dest='verbose')
	cmd_parsers = top_parser.add_subparsers(title='subcommands',
											description='bestbets')
	bbet_parser = cmd_parsers.add_parser('bestbets',
		help='''Find best bets by comparing FiveThirtyEight prediction models to 
				multiple sportsbooks from Vegas Insider'''
	)
	bbet_parser.add_argument('-l', '--league', '--leagues', 
							nargs='+',
							dest='leagues',
							help='Search only for lines specific to a league -- e.g., MLB, NFL, etc')
	bbet_parser.add_argument('-b', '--sportsbooks', 
							nargs='+',
							dest='books',
							help='Search only for lines from a specific sportsbook')
	bbet_parser.set_defaults(func=cmd.best_bets)
	
	args = top_parser.parse_args()
	if args.verbose:
		setup_logging()
	args.func(league=args.leagues, sportsbooks=args.books)
	
	