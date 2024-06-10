import nba_api.stats.static.players

# Pipe
from sklearn.pipeline import Pipeline

# Preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Ridge

# SMOTE
from imblearn.over_sampling import SMOTE

import pandas as pd


# Evaluation
class modelNBA:
    def __init__(self, df, rookie=False, use_ridge=False):
        self.players = self.get_all_players()
        self.use_ridge = use_ridge
        self.df = df
        if rookie: self.df = self.df[(self.df['ROOKIE'] > 0)]


        # Prepare input vector
        self.X = self.df.copy()

        if not rookie:
            self.X = self.X[self.X['ROOKIE'] == 0]

        # Prepare output vector
        # also convert representation of TEAM_NUMBER, where 0 means not qualified, ant the bigger the number the better the team 
        if rookie:

            self.X['ALL_ROOKIE_TEAM_NUMBER'] = self.X['ALL_ROOKIE_TEAM_NUMBER'].replace({1: 2, 2: 1})
            self.X['ALL_ROOKIE_TEAM_NUMBER'] = self.X['ALL_ROOKIE_TEAM_NUMBER'].fillna(0) 
            self.y = self.X[['ALL_ROOKIE_TEAM_NUMBER']].copy()
            
        else:
            self.X['ALL_NBA_TEAM_NUMBER'] = self.X['ALL_NBA_TEAM_NUMBER'].replace({1: 3, 3: 1})
            self.X['ALL_NBA_TEAM_NUMBER'] = self.X['ALL_NBA_TEAM_NUMBER'].fillna(0) 
            
            self.y = self.X[['ALL_NBA_TEAM_NUMBER']].copy()

        # convert season to 4 digit representation
        self.X['SEASON'] = self.X['SEASON'].str[:4]

        # Drop non-relevant columns
        self.X = self.X.drop(columns=['FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FT_PCT', 'OREB', 'BLKA', 'PF', 'GP'])
        
        # Remove unecessary columns from input vector
        self.X = self.X.drop(columns=['ALL_ROOKIE_TEAM_NUMBER', 'ROOKIE', 'ALL_NBA_TEAM_NUMBER'])

        #SMOTE
        smote = SMOTE(random_state=42, k_neighbors=5)
        self.X_smote, self.y_smote = smote.fit_resample(self.X, self.y)
        
    def train(self):
        X_train, X_test, y_train, y_test = train_test_split(self.X_smote.values, self.y_smote.values.ravel(), test_size = 0.1, stratify=self.y_smote.values.ravel(), random_state=42)

        if self.use_ridge:
            self.model = Pipeline([
                ('scaler', StandardScaler()), 
                ('ridge', Ridge(alpha=1.0))
            ])
        else:
            self.model = Pipeline([
                ('scaler', StandardScaler()), 
                ('logreg', LogisticRegression(C=10, max_iter=500))
            ])

        self.model.fit(X_train, y_train) 

    def predict(self, season, player_num):
        X = self.X[(self.X['SEASON'] == season)]

        # Remove players that have less than 20 minutes average played time in game, since noone won all_nba like that
        X = X[X['MIN'] > 20.0]
        
        # Predict and get top players
        y = self.model.predict(X.values)

        X['ALL_NBA_SCORE'] = y
        X_sorted = X.sort_values(by='ALL_NBA_SCORE', ascending=False)
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
