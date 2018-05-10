import re
import logging

import requests
from bs4 import BeautifulSoup

from ..bet import Sportsbook, Line

logger = logging.getLogger(__name__)

class VegasInsider:
	def __init__(self):
		self.bases = ['http://www.vegasinsider.com/mlb/odds/las-vegas/line-movement',
					  'http://www.vegasinsider.com/mlb/odds/offshore/line-movement']
		self.books = []
		
	def build_line_history(self, matchups, date):
		day = str(date.day).zfill(2)
		month = str(date.month).zfill(2)
		year = str(date.year)[-2:]
		
		for page in self.bases:
			for away, home in matchups:
				away = away.replace(' ', '-')
				home = home.replace(' ', '-')
				site = '/{}-@-{}.cfm/date/{}-{}-{}'.format(away, home, month, day, year)
		
				r = requests.get(page + site)
				soup = BeautifulSoup(r.text, 'html.parser')
		
				bookie_tables = soup.find('div', {'SLTables1'}).find_all('table', recursive=False)[2:]
		
				for bookie in bookie_tables:
					name = bookie.find('tr', {'class':'component_head'}).text
					name = clean_name(name)
					if name == 'VI CONSENSUS':
						continue  # this is not an actual sportsbook
			
					sportsbook = self.find_sportsbook(name)
					if sportsbook is None:
						sportsbook = Sportsbook(name)
						self.books.append(sportsbook)
						logger.debug('Added {}'.format(name))
				
					rows = bookie.find('table', {'class':'rt_railbox_border2'}).find_all('tr')[2:]
					self.scrape_moneylines(rows, sportsbook)				
			
	def find_sportsbook(self, name):
		for book in self.books:
			if name.lower() == book.name.lower():
				return book
				
	def get_line_history_by_sportsbook(self, team, book_name=None):
		if book_name is not None:
			sportsbook = self.find_sportsbook(book_name)
			return sportsbook.get_line_history(team)
		
		lines = {}
		for book in self.books:
			lines[book] = book.get_line_history(team)
		return lines
						
	@staticmethod	
	def scrape_moneylines(html_table, sportsbook):
		for row in html_table:
			for t in row.find_all('td')[2:4]:
				t = clean_name(t.text)
				sign_pos = re.search(r'\+|-', t)
				if sign_pos is None:
					continue  # no line in this row
				sign_pos = sign_pos.start()
				odds = int(t[sign_pos:])
				team = t[:sign_pos]
				sportsbook.add_line(Line(team, odds))
			
			
def clean_name(name):
	return name.replace('\t', '').replace('\n', '').replace('\r', '').replace(' LINE MOVEMENTS', '')