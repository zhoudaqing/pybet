from pybet.webscrapers import fivethirtyeight


def get_model(name):
    name = name.lower()
    return MODELS[name]()


class Model:
    def __init__(self, scrapers, name):
        self.scrapers = scrapers
        self.name = name

    def get_todays_predictions(self, league):
        raise NotImplementedError

    def get_scraper(self, league):
        try:
            scraper = self.scrapers[league.lower()]
        except KeyError:
            msg = 'This model does not currently implement a scraper for {}'
            raise KeyError(msg.format.format(league))
        return scraper()

    def supported_wagers(self):
        raise NotImplementedError


class FiveThirtyEight(Model):
    def __init__(self):
        scrapers = {'mlb': fivethirtyeight.BaseballScraper,
                    'nba': fivethirtyeight.BasketballScraper}

        super().__init__(name='FiveThirtyEight', scrapers=scrapers)

    def get_todays_predictions(self, league):
        scraper = super().get_scraper(league)
        return scraper.scrape_todays_games()

    def supported_wagers(self, league):
        supported = {'nba': ['moneyline', 'spread'],
                     'mlb': ['moneyline']}
        return supported[league]

    def __str__(self):
        return 'FiveThirtyEight'


MODELS = {'fivethirtyeight': FiveThirtyEight}
