import pandas as pd
from scraper.nlp_extractor import extract_language_features
from scraper.model import fit_predict
import yfinance as yf

# load news data acquired from wsj_scraper.py
news = pd.read_csv('data/wsj_2018_2020.csv', 
parse_dates=['date'])

# we don't need all the columns, lets keep only some of them
keep = ['Business','U.S.','Letters','World','Commentary','Heard on the Street',
'Politics','Review & Outlook','Finance','Tech','Europe','Markets','Earnings','Asia',
'China','U.S. Economy','CFO Journal']

news = news[news.subject.isin(keep)]

# extract features that can be used for predicting stock prices from news text
features = extract_language_features(news, select_top_features = None, method = 'count', ngrams = (1,2))

OIL = yf.Ticker("CL=F")
DJI = yf.Ticker("^DJI")
TESLA = yf.Ticker("TSLA")

# see terminal output for results
model, importances = fit_predict(features, OIL, model = 'boosting')
model, importances = fit_predict(features, DJI, model = 'boosting')
model, importances = fit_predict(features, TESLA, model = 'boosting')
