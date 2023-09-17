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

def extract_language_features(news: pd.DataFrame, select_top_features: int = None, method = 'count', ngrams = (1,1)):
    '''
    columns = ['date', 'headline']
    '''

    corpus = news.groupby('date').agg({'headline': ' '.join})

    if method == 'count':
        vectorizer = CountVectorizer(preprocessor=preprocess,stop_words='english',ngram_range=ngrams)
    counts = vectorizer.fit_transform(corpus.headline.values)
    counts = pd.DataFrame(counts.toarray())
    counts.columns = vectorizer.get_feature_names_out()

    if select_top_features != None:
        total_counts = counts.sum()
        top_features = total_counts[total_counts > select_top_features].index
        features = counts.loc[:,top_features]

    else:
        features = counts
    
    features.index = corpus.index

    return features

