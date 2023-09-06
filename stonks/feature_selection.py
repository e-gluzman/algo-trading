import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import SelectFromModel
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score
from sklearn.feature_selection import RFE, RFECV, SequentialFeatureSelector, mutual_info_classif
from sklearn.preprocessing import MinMaxScaler
from genetic_selection import GeneticSelectionCV

def chat_gpt_select_from_model():
    # Load the data into a pandas dataframe
    data = pd.read_csv('your_data.csv')

    # Split the data into features and target
    X = data.drop('target', axis=1)
    y = data['target']

    # Create a DecisionTreeClassifier object
    dt = DecisionTreeClassifier()

    # Create a dictionary of hyperparameters to search over
    params = {'max_depth': [3, 5, 7],
            'min_samples_leaf': [10, 20, 30]}

    # Create a custom scoring function to optimize for precision and recall
    scoring = {'precision': make_scorer(precision_score),
            'recall': make_scorer(recall_score)}

    # Use SelectFromModel to perform feature selection
    sfm = SelectFromModel(dt)

    # Use GridSearchCV to search over the hyperparameters and perform feature selection
    grid = GridSearchCV(sfm, params, cv=5, scoring=scoring, refit='recall')
    grid.fit(X, y)

    # Print the best hyperparameters and selected features
    print("Best hyperparameters:", grid.best_params_)
    print("Selected features:", X.columns[grid.best_estimator_.get_support()])

    # Get the best estimator from GridSearchCV
    best_dt = grid.best_estimator_.estimator_

    # Fit the best estimator on the selected features
    best_dt.fit(X[X.columns[grid.best_estimator_.get_support()]], y)

def genetic_chat_gpt():
    from sklearn.tree import DecisionTreeClassifier
    from mlxtend.feature_selection import GeneticAlgorithmSelector
    import numpy as np

    # Define your dataset and target
    X = np.random.rand(100, 20) # example dataset
    y = np.random.randint(0, 2, 100) # example target

    # Define your model
    clf = DecisionTreeClassifier()

    # Define the selector with a genetic algorithm
    selector = GeneticAlgorithmSelector(clf,
                                        n_gen=10,
                                        size=50,
                                        verbose=2,
                                        scoring='accuracy',
                                        cv=5)

    # Fit the selector to your dataset and target
    selector.fit(X, y)

    # Get the selected features
    selected_features = X[:, selector.support_]


def select_best_features(hist, method = 'RFE', estimator_type = 'tree', class_weight = None, max_depth = None, n_features_to_select = 15,
                         normalisation=None, step = 1):

    # try scoring = 'f1_score'
    # SequentialFeatureSelector backwards, forwards

    #data = hist.drop(columns = ['exchange','symbol']).dropna().copy()
    data = hist.dropna()
    #X = data.loc[:,model_features].drop(columns = ['barrier'])
    X = data.drop(columns = ['barrier'])
    y = data.barrier
    if normalisation == 'min_max':
        scaler = MinMaxScaler()
        X = scaler.fit_transform(X)
    if estimator_type == 'tree':
        estimator = DecisionTreeClassifier(max_depth = max_depth, class_weight=class_weight)
    elif estimator_type == 'random_forest':
        estimator = RandomForestClassifier(max_depth = max_depth, class_weight=class_weight, n_jobs = -1)

    if method == 'RFE':
        rfe = RFE(estimator=estimator, n_features_to_select=n_features_to_select, step=step, verbose=1)
        rfe.fit(X, y)
        ranking = rfe.ranking_
        #print(pd.Series(ranking,index=X.columns).sort_values().head(10).index)
        #return pd.Series(ranking,index=X.columns)
        return ranking
    
    elif method == 'RFECV':
        rfe = RFECV(estimator=estimator, step=step, n_jobs=-1)
        rfe.fit(X, y)
        ranking = rfe.ranking_
        print(pd.Series(ranking,index=X.columns).sort_values().head(10).index)
        return pd.Series(ranking,index=X.columns)
    
    elif method == 'mutual_information':
        ranking = mutual_info_classif(X,y)
        ranking = pd.Series(ranking,index=X.columns)
        return ranking
    
    elif method == 'genetic':
        # 260 min for this - ['macd_5_8', 'macd_8_26', 'macd_20_60_signal', 'macd_1500_15000_signal',
        # 'macd_60_1440', 'ATR_14', 'ATR_50', 'vol_std_100', 'vol_std_50']

        scorer = make_scorer(f1_score)

        model = GeneticSelectionCV(
            estimator, cv=3, verbose=1,
            scoring=scorer, max_features=15,
            n_population=100, crossover_proba=0.5,
            mutation_proba=0.2, n_generations=50,
            crossover_independent_proba=0.5,
            mutation_independent_proba=0.04,
            tournament_size=3, n_gen_no_change=10,
            caching=True, n_jobs=-1)
        
        model = model.fit(X, y)
        return model 
        #print('Features:', X.columns[model.support_])

    elif method == 'select_from_model':
        # from sklearn.feature_selection import SelectFromModel
        # from sklearn.ensemble import RandomForestClassifier

        # embeded_rf_selector = SelectFromModel(RandomForestClassifier(n_estimators=100), max_features=num_feats)
        # embeded_rf_selector.fit(X, y)

        # embeded_rf_support = embeded_rf_selector.get_support()
        # embeded_rf_feature = X.loc[:,embeded_rf_support].columns.tolist()
        # print(str(len(embeded_rf_feature)), 'selected features')
        print('meow')

    # model_features = ranking.smth
    # if fit_new_features == True:
    #     ypred, model_index = models.predict_barrier(hist, features = model_features, max_depth=max_depth, model_type=estimator_type, parallel=True)

