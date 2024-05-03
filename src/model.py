# Pipe
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

# Preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Models
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.dummy import DummyClassifier
from sklearn.neighbors import KNeighborsClassifier

# Voting
from sklearn.ensemble import VotingClassifier

# Evaluation
from sklearn.metrics import confusion_matrix, classification_report

class modelNBA:
    def __init__(self, df):
        self.df = df

        self.y = df[['ALL_NBA_TEAM_NUMBER']]
        self.y = self.y.fillna(0.0)
        self.y = self.y.astype(int)
        self.X = self.df.drop(columns=['ALL_ROOKIE_TEAM_NUMBER', 'ROOKIE', 'ALL_NBA_TEAM_NUMBER'])
        self.X['SEASON'] = self.X['SEASON'].str[:4]
        
        self.X = self.X.values
        self.y = self.y.values.ravel()

    def train(self):

        voting_clf_models = [ 
                ('k', Pipeline([('scaler', StandardScaler()), ('k', KNeighborsClassifier())])),
                ('tree', Pipeline([('tree', DecisionTreeClassifier(random_state=42))])),
                ('log_reg', Pipeline([('scaler', StandardScaler()), ('log_reg', LogisticRegression(random_state=42, max_iter=1000, solver='saga'))])),
                ('random_forest', Pipeline([('random_forest', RandomForestClassifier(random_state=42))]))
                ]
        models = [ Pipeline([('random', DummyClassifier(random_state=42, strategy="uniform"))]),
                  VotingClassifier(estimators=voting_clf_models)
                ]
        
        names = ['random', 'voting']

        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size = 0.1, stratify=self.y, random_state=42)
        for name, model in zip(names, models):
            model.fit(X_train, y_train) 
            y_pred = model.predict(X_test)

            report = classification_report(y_test, y_pred, output_dict=False, zero_division=0.0) 
            print(name)
            print(report)