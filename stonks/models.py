from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, precision_score, accuracy_score, recall_score, f1_score
from sklearn.preprocessing import MinMaxScaler
import joblib
from joblib import Parallel, delayed
from xgboost import XGBClassifier
from datetime import datetime, timedelta

#import dask.dataframe as dd
# from dask_ml.model_selection import train_test_split
# from dask_ml.metrics import accuracy_score
#from dask_ml.xgboost import XGBClassifier

import pandas as pd

def predict_barrier(
        hist,
        features,
        max_depth = 4,
        class_weight=None,
        model_type='tree',
        normalise=None,
        parallel=False,
        tree_method = None,
        prob_thresh = None,
        split_size = 0.9,
        backtest_days = 30,
        sample = False,
        sampling_rate = 4,
        prod_model = False
        ):
    
    hist = hist.loc[:,features]
    hist = hist.dropna()

    #hist.barrier = hist.barrier.apply(lambda x: int(x))

    hist['target'] = hist.barrier

    # get rows from our sample from unbalanced class
    if sample == True:
        if hist.barrier.nunique() == 3:
            sample_index2 = list(hist.loc[hist.barrier==0].index)
            sample_index1 = list(hist.loc[hist.barrier==1].iloc[::sampling_rate, :].index)
            sample_index3 = list(hist.loc[hist.barrier==2].index)
            sample_index = sample_index1+sample_index2+sample_index3
        elif hist.barrier.nunique() == 2:
            sample_index1 = list(hist.loc[hist.barrier==0].iloc[::sampling_rate, :].index)
            sample_index3 = list(hist.loc[hist.barrier==1].index)
            sample_index = sample_index1+sample_index3

    X = hist.drop(columns=['target','barrier'])
    #X = hist.drop(columns=['target','exchange','symbol'])
    #X = data.drop(columns=['target','forward_sma10','exchange','symbol'])
    y = hist.target

    if normalise == 'min_max':
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)

    split_index = len(X)*split_size
    backtest_start_date = (X.index[-1] - timedelta(days=backtest_days)).replace(hour=0)
    #backtest_hist.loc[backtest_hist.index > backtest_start_date]
    if sample == True:
        X_train = X.loc[(X.index <= str(X.index[int(split_index)].date())) & (X.index.isin(sample_index))]
        X_test = X.loc[X.index > str(X.index[int(split_index)].date())]
        y_train = y.loc[(X.index <= str(X.index[int(split_index)].date())) & (X.index.isin(sample_index))]
        y_test = y.loc[X.index > str(X.index[int(split_index)].date())]
    else:
        # X_train = X.loc[X.index <= str(X.index[int(split_index)].date())]
        # X_test = X.loc[X.index > str(X.index[int(split_index)].date())]
        # y_train = y.loc[X.index <= str(X.index[int(split_index)].date())]
        # y_test = y.loc[X.index > str(X.index[int(split_index)].date())]
        X_train = X.loc[X.index <= backtest_start_date]
        X_test = X.loc[X.index > backtest_start_date]
        y_train = y.loc[X.index <= backtest_start_date]
        y_test = y.loc[X.index > backtest_start_date]

    if model_type == 'tree':
        model = DecisionTreeClassifier(max_depth=max_depth, class_weight=class_weight)
    elif model_type == 'random_forest':
        model = RandomForestClassifier(max_depth=max_depth, class_weight=class_weight)
        if parallel == True:
            model = RandomForestClassifier(max_depth=max_depth, n_jobs=-1, class_weight=class_weight)
    elif model_type == 'boosting':
        model = GradientBoostingClassifier(max_depth = max_depth)
        if parallel == True:
            model = XGBClassifier(max_depth=max_depth, n_jobs=-1, tree_method = tree_method)


    

    # if parallel == True:
    #     with joblib.parallel_backend(backend='loky', n_jobs=-1):
    #         model.fit(X_train, y_train)
    # else:
    #     model.fit(X_train, y_train)

    model.fit(X_train, y_train)

    if prob_thresh == None:
        ypred=model.predict(X_test)
    else:
        ypred=model.predict_proba(X_test)
        return ypred, y_test.index, model
    print(classification_report(y_pred=ypred,y_true=y_test))

    if prod_model:
        model.fit(X, y)
        ypred=model.predict(X)
        print('Returning production model with no test or eval set')
        print(classification_report(y_pred=ypred,y_true=y))

    #print(pd.DataFrame(model.feature_importances_,index=X_train).columns).sort_values(by=0,ascending=False).head(10)

    return ypred, y_test.index, model