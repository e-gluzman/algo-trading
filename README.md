# ML algo trading
## Project description

In this project, I am showcasing my module for developing machine learning models for day algorithmic trading on 1-minute bars. The main module '/stonks' contains functions for extracting features from stock price data (bars), feature selection, labelling target variables, training the model and backtesting. So far I have managed to hit up to 10% monthly (~300% year) returns in backtests on a single stock.

The '/scraper' folder also contains a web scraping algorithm I wrote for Wall Street Journal headlines and analysing their relationship to stock and commodity prices.

#### How to run this

First, read the project description below and check out the 'trading_ml_model_showcase' notebook'. It will walk you through stages of creating an ML model for trading, from feature extraction to backtesting. 

You can also have a look at the 'web_scraper_demonstration' script. It models the effect of news headlines on stock and commodity prices.

## Highlights

### Feature extraction

The first stage is extracting features from time series price data. For that I use common techincal indicators such as exponential moving averages (EMA), moving average convergence divergence (MACD), RSI, ATR etc. I normalise these indicators to express them in terms of standard deviations or percentage change relative to stock price in time window X. Then I iterate over a large list of time windows to create hundreds of features to be used in model development.

For example:
* macd_12_26 is the moving average convergence divergence comparing the 12 minute and 26 minute EMA of the Close price
* macd_12_26_pct? is the same indicator but expressed as pct % of the 12 minute EMA.
* volume_macd_100_1000 is the MACD for 100 and 1000 minute time windows calculated based on Volume.
* vol_std_pct_50 is a volatility metric based on an exponential rolling mean of standard deviaton over 50 minutes, expressed as pct
etc.

(see stonks/feature_extraction.py)

### Labelling and stop-loss/ take-profit levels

In order to use machine learning for trading we need to label desirable outcomes such as a predicted stock price increase to generate buy signals. The best method I have found for this so far is the tripple barrier method (see Lopez de Prado, financial advances in machine learning). The triple barrier method labels bars based on whether the stock price will move up and hit a certain price "barrier" first, a lower barrier or neither within a certain time window.

I calculate the expected volatility within a certain time range (e.g. 50 minutes) based on recent history e.g. over the last 3 days. I then use it do dynamically set profit/ loss targets for training the ML model and as stop-loss/ take-profit levels in backtesting.

(see stonks/labelling.py)

### Feature selection

The next stage is selecting the best features from the hundreds available. This can be done based on common sense or algorithmically. This package supports automated feature selection with recursive feature elimination (RFE), genetic algorithms and mutual information. At the moment I like using RFE with random forests, and then picking features that make sense to me for model development.

(see stonks/feature_selection.py)

### Model training

At the moment I am using a standard gradient boosting algorithm (XGBoost) to train the model, as it seems to perform well assuming well-selected features. This package also supports logistic regression and random forests (useful for feature selection). I have also tested LSTM networks for modelling, but at the moment XGBoost outperforms them.

(see stonks/models.py)


### Backtesting

The backtesting function takes in a dataframe of bars that we put aside for testing before model training. We pass it a time series of buy decisions based on ML model output. It also has optional parameters such as:
* a time series of sell signals based on ML model output
* stop loss and take profit levels time series, with options to sell above/ below those levels
* hold_on_buy - allows to hold on to stock as long as we have a new buy signal
* holding_period - how long to hold a stock if there is no sell signal or the stop loss level was not crossed
* starting cash
* updating stop loss and take profit levels

We set the stop loss and take profit levels dynamically using the same method we used for labelling (expected volatility within a certain time range (e.g. 50 minutes) based on recent history).

(see stonks/backtest.py)

### Results and next steps

So far the best (plausible) results I have hit in backtests are returns of 10% per month (300% per year) on the Palantir (PLTR) stock. This strategy has a winrate of 28%, with an average win size of 1.5% and loss size of 0.66%

I have also hit much higher returns (1000% + per year) on strategies making hundreds of small (<= 1$ price difference) trades per day, but I rule these out (for now) because of high volume, slippage and limited execution speed.

At the moment I am deploying these strategies on a Cloud Server and testing them using the Alpaca API brokerage. However, models like this tend to decay rapidly with changing market conditions. Because of this I am currently automating the process of iterating over hundreds of such strategies with different features, time windows and stocks and deploying the highest performing models.

If you would like to know more, please contact me at:
email: gluzman64@gmail.com
linkedin: 
whatsapp: +447463457579

### Extra: Web scraping and natural language processing

When I started this project I also wrote a web scraping script that may be used to predict stock prices based on news headlines. I have scraped Wall Street Journal headlines and trained an XGBoost regressor to see which words (or ngrams) predict Closing prices for stocks and commodities.

Here are some interesting results showing most important features from 2022:

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