# ML algo trading
## Project description

In this project, I am showcasing my module for developing machine learning models for day algorithmic trading on 1-minute bars. The main module '/stonks' contains functions for extracting features from stock price data (bars), feature selection, labelling target variables, training the model and backtesting. So far I have managed to hit up to 10% monthly (~300% year) returns in backtests on a single stock.

The '/scraper' folder also contains a web scraping algorithm I wrote for Wall Stree Journal headlines and analysing their relationship to stock and commodity prices.

#### How to run this

First, read the project description below and check out the 'trading_ml_model_showcase' notebook'. It will walk you through stages of creating an ML model for trading, from feature extraction to backtesting. 

You can also have a look at the 'web_scraper_demonstration' script. It models the effect of news headlines on stock and commodity prices.

## Highlights

### Feature extraction

The first stage is extracting features from time series price data. For that I use common techincal indicators such as exponential moving averages (EMA), moving average convergence divergence (MACD), RSI, ATR etc. I normalise these indicators to express them in terms of standard deviations or pct_change relative to stock price in time window X. Then I iterate over a large list of time windows to create hundreds of features to be used in model development.

For example:
macd_12_26 is the moving average convergence divergence comparing the 12 minute and 26 minute EMA of the Close price
macd_12_26_pct? is the same indicator but expressed as pct % of the 12 minute EMA.
volume_macd_100_1000 is the MACD for 100 and 1000 minute time windows calculated based on Volume.
vol_std_pct_50 is a volatility metric based on an exponential rolling mean of standard deviaton over 50 minutes, expressed as pct
etc.

### Labelling

In order to use machine learning for trading we need to label desirable outcomes such as a predicted stock price increase to generate buy signals. The best method I have found for this so far is the tripple barrier method (see Lopez de Prado, financial advances in machine learning).
### Feature selection

The next stage is selecting

### Model training

### Backtesting

We can set the SLTP using the same method we used for labelling

### Results


### Web scraping and natural language processing

I have predicted the Closing price for stocks and commodities obtained from the yfinance module/ API. I have only used the text features extracted from WSJ articles. 

So far the best result I have obtained is an R^2 score of **0.80** for Tesla stock using a Gradient Boosting Regressor.

UPDATE: adding ngrams (bigrams) to the model have improved performance up to R^2 score = **0.89**

The feature importances for this model also make sense:

| Features affecting TSLA closing price | Importance |
|---------------------------------------|------------|
| coronavirus                           | 0.605510   |
| covid                                 | 0.099173   |
| biden                                 | 0.023690   |
| police                                | 0.017917   |
| best                                  | 0.017619   |
| global                                | 0.015676   |
| outbreak                              | 0.015082   |
| virus                                 | 0.014075   |
| recovery                              | 0.011028   |
| cash                                  | 0.010030   |


For contrast, here are the feature importances for the Dow Jones Industrial Average Index model:


| Features affecting DJI closing price | Importance |
|--------------------------------------|------------|
| impeachment                          | 0.188133   |
| shutdown                             | 0.049280   |
| covid                                | 0.030695   |
| max                                  | 0.030448   |
| response                             | 0.029124   |
| stimulus                             | 0.024821   |
| cash                                 | 0.021961   |
| dollar                               | 0.019271   |
| crisis                               | 0.016630   |
| day                                  | 0.016275   |


This is an early demo, and I will keep improving this project!

### Next steps

I have currently deployed the algorithm with Alpaca + Google Cloud and I am working on a strategy optimiser.