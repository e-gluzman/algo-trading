from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import pandas as pd

def fit_predict(news_features, ticker, type='tree'):
    
    target_name = ticker.info['shortName']
    y = ticker.history(period='5y').loc[:,['Close']]
    X = pd.merge(news_features, y, how='inner', left_index= True, right_index=True)
    y = X.Close.values
    X.drop(columns=['Close'],inplace=True)

    X_train, X_test, y_train, y_test = train_test_split(X,y,random_state=1)
    
    print(f'Training model for target - {target_name}')
    print(f'Model type - {type}:')

    if type == 'tree':
        model = DecisionTreeRegressor()
        model.fit(X_train,y_train)
        ypred = model.predict(X_test)
        r2 = r2_score(y_test,ypred)
        mae = mean_absolute_error(y_test,ypred)
        importances = pd.DataFrame(model.feature_importances_,index=X.columns).sort_values(by=0,ascending=False)

    if type == 'boosting':
        model = GradientBoostingRegressor()
        model.fit(X_train,y_train)
        ypred = model.predict(X_test)
        r2 = r2_score(y_test,ypred)
        mae = mean_absolute_error(y_test,ypred)
        importances = pd.DataFrame(model.feature_importances_,index=X.columns).sort_values(by=0,ascending=False)

    print(f'Model results for target - {target_name}:')
    print('')
    print('r2_score: ' + str(r2))
    print('mean_absolute_error: ' + str(mae))
    print('')
    print('Most important features for predicting this variable:')
    print(importances.head(10))
    print('')

    return model, importances