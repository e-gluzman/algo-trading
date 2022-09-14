# financial-market-forecast
Predicting prices for stocks and commodities

## Project description

In this project, I wanted to explore using alternative data to forecast the prices of stocks and commodities. I built a web scraper that parses articles from the Wall Street Journal archive. I extracted features from the text and used them to forecast prices for Oil, Dow Jones Industrial Average index and Tesla stock. 

## Highlights/ How to run this

So far the most interesting part of the project is the web scraper I created for the WSJ archive. You can check it out if you clone the repository and run it from scrapers/wsj_scraper.py

Once the scraper saves the result to /data you can run the feature extractors and the ML models from run.py

## Results

I have predicted the Closing price for stocks and commodities obtained from the yfinance module/ API. I have only used the text features extracted from WSJ articles. 

So far the best result I have obtained is an R^2 score of <mark style="background-color:red">0.80</mark> for Tesla stock using a Gradient Boosting Regressor. 

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