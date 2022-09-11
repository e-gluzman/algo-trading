from nltk.corpus import stopwords
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd

def preprocess(string):
    
    string = string.lower()
    
    string = re.sub('b\'', '', string)
    
    string = re.sub('b\"', '', string)

    string = re.sub('[!@#$.1-9-\(\)\0:\'\"0]', '', string)

    #string = string.split(' ')
    #string = [s for s in string if s not in stopwords.words('english')]
    #string.remove('')
    #string = ' '.join(string)
    
    return string

def extract_language_features(news: pd.DataFrame, select_top_features: int = 100, method = 'count'):
    '''
    columns = ['date', 'headline']
    '''

    corpus = news.headline

    if method == 'count':
        vectorizer = CountVectorizer(preprocessor=preprocess,stop_words='english')
    counts = vectorizer.fit_transform(corpus.values)
    counts = pd.DataFrame(counts.toarray())
    counts.columns = vectorizer.get_feature_names_out()

    total_counts = counts.sum()
    top_features = total_counts[total_counts > select_top_features].index

    if select_top_features != 'None':
        features = counts.loc[:,top_features]
    
    dates = news.date
    features['date'] = dates.reset_index(drop=True)
    features = features.groupby('date').max()

    return features

