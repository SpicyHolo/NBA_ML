# Pipe
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import Pipeline

# Preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

import nba_api.stats.static.players

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
import pandas as pd
class modelNBA:
    def __init__(self, df, rookie=False, exclude_rookies=False):
        self.players = self.get_all_players()
        self.rookie = rookie

        self.df = df
        if rookie: self.df = self.df[(self.df['ROOKIE'] > 0)]

        # Prepare input vector
        self.X = self.df.copy()

        if exclude_rookies:
            self.X = self.X[self.X['ROOKIE'] == 0]

        # Preapre output vector
        if rookie:
            self.y = self.X[['ALL_ROOKIE_TEAM_NUMBER']].copy()
            self.y['ALL_ROOKIE_TEAM_NUMBER'] = (self.y['ALL_ROOKIE_TEAM_NUMBER'] > 0).astype(int)

        else:
            self.y = self.X[['ALL_NBA_TEAM_NUMBER']].copy()
            self.y['ALL_NBA_TEAM_NUMBER'] = (self.y['ALL_NBA_TEAM_NUMBER'] > 0).astype(int)

        # Remove unecessary columns from input vector
        self.X = self.X.drop(columns=['ALL_ROOKIE_TEAM_NUMBER', 'ROOKIE', 'ALL_NBA_TEAM_NUMBER'])
        self.X['SEASON'] = self.X['SEASON'].str[:4]


    def train(self):
        X_train, X_test, y_train, y_test = train_test_split(self.X.values, self.y.values.ravel(), test_size = 0.1, stratify=self.y.values.ravel(), random_state=42)
        self.model =  Pipeline([('random_forest', RandomForestClassifier(random_state=42))])
        self.model.fit(X_train, y_train) 
        y_pred = self.model.predict(X_test)

    def predict(self, season, player_num):
        X = self.X[(self.X['SEASON'] == season)]
        

        y = self.model.predict_proba(X.values)
        y = y[:, 1]
        X['ALL_NBA_PROB'] = y
        X_sorted = X.sort_values(by='ALL_NBA_PROB', ascending=False)
        head = X_sorted.head(player_num)
        head['NAME'] = head.apply(self.get_player_name, axis=1)
        return head

    def get_all_players(self):
        all_players = nba_api.stats.static.players.get_players()

        # Convert the list of dictionaries to a DataFrame
        players_df = pd.DataFrame(all_players)
        return players_df 

    def get_player_name(self, row):
        player_id = row['PLAYER_ID']
        data = self.players[(self.players['id'] == player_id)]

        if data.empty:
            return None
        else:
            data = data.to_dict(orient='records')[0]  
            return data['full_name']
