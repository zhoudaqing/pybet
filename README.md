# Pybet (Work in Progress)
A command line tool for finding the best MLB and NBA odds from multiple onshore and offshore sportsbooks compiled by Vegas Insider based on FiveThirtyEight prediction models.

## Theory

The best straight-up moneyline odds are found by comparing the model's predicted win probability against the implied win probability expressed by the odds offered by the sportsbook.

For example,

FiveThirtyEight predicts the Giants have a 42% chance to win. Odds are offered from the following sportsbooks (implied win probability in parenthesis):

```
Sportsbook A: +140 (41.66%)
Sportsbook B: +135 (42.55%)
Sportsbook C: +144 (40.98%)
```

Pybet will identify Sportsbook C as offering the best odds based on an expected value of roughly 2.5% (the model's estimated win probability in excess of the odds). 

Alternatively, the Pirates are given a 59% chance to win. Odds are offered from the following sportsbooks:

```
Sportsbook A: -148 (59.6%)
Sportsbook B: -150 (60%)
Sportsbook C: -145 (59.18%)
```

None of these sportsbooks offer positive value as their implied win probabilities are greater than what the model predicts. They are excluded from the output.

Point spread bets, including runlines, are still a work in progress.

This is a proof of concept and should not be used with the expectation of making a profit. Currently only FiveThirtyEight MLB and NBA predictions are scraped, but Massey Ratings are planned for a future release.

## Usage
```
pybet bestbets [-b [--sportsbooks]] [-l [--leagues]]

optional arguments:
-l, --leagues
            Search only for lines specific to a league -- e.g., MLB, NBA
            
-b, --sportsbooks
            Search only for lines from specific sportsbooks as listed on VegasInsider

```


## More info coming soon...