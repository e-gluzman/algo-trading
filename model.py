from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score
import pandas as pd

def fit_predict(news_features, ticker, model='tree'):

    X = pd.merge(news_features, ticker, how='inner', left_index= True, right_index=True)
    y = X.Close.values
    X.drop(columns=['Close'],inplace=True)

    X_train, X_test, y_train, y_test = train_test_split(X,y,random_state=1)

    if model == 'tree':
        model = DecisionTreeRegressor()
        model.fit(X_train,y_train)
        ypred = model.predict(X_test)
        r2 = r2_score(y_test,ypred)
        importances = pd.DataFrame(model.feature_importances_,index=X.columns).sort_values(by=0,ascending=False)

    if model == 'boosting':
        model = GradientBoostingRegressor()
        model.fit(X_train,y_train)
        ypred = model.predict(X_test)
        r2 = r2_score(y_test,ypred)
        importances = pd.DataFrame(model.feature_importances_,index=X.columns).sort_values(by=0,ascending=False)

    return model, r2, importances