import pandas as pd
from nlp_extractor import extract_language_features
from model import fit_predict
import yfinance as yf

# load news data acquired from wsj_scraper.py
news = pd.read_csv('data/wsj_2018_2020.csv')

# we don't need all the columns, lets keep only some of them
keep = ['Business','U.S.','Letters','World','Commentary','Heard on the Street',
'Politics','Review & Outlook','Finance','Tech','Europe','Markets','Earnings','Asia',
'China','U.S. Economy','CFO Journal']

news = news[news.subject.isin(keep)]

# extract features that can be used for predicting stock prices from news text
features = extract_language_features(news, select_top_features = 100, method = 'count')

print(features)

# lets choose a few targets for prediction.
OIL = yf.Ticker("CL=F").history(period='5y')
DJI = yf.Ticker("^DJI").history(period='5y')

model, r2, importances = fit_predict(features,OIL.Close)

print('Oil result')
print('r2_score: ' + str(r2))
print(importances.head(10))

model, r2, importances = fit_predict(features,DJI.Close)

print('Dow Jones Industrial Average result')
print('r2_score: ' + str(r2))
print(importances.head(10))