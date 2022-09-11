import pandas as pd
from nlp_extractor import extract_language_features


# load news data acquired from wsj_scraper.py
news = pd.read_csv('data/wsj_2018_2020.csv')

# we don't need all the columns, lets keep only some of them

keep = ['Business','U.S.','Letters','World','Commentary','Heard on the Street',
'Politics','Review & Outlook','Finance','Tech','Europe','Markets','Earnings','Asia',
'China','U.S. Economy','CFO Journal']

news = news[news.subject.isin(keep)]

# extract features that can be used in prediction from news text
features = extract_language_features(news, select_top_features = 100, method = 'count')

print(features)