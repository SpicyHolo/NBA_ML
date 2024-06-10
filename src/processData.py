from datetime import datetime
import pandas as pd
from tqdm import tqdm

import nba_api.stats.static.players

class processData:
    def __init__(self, dir):
        self.seasons = self.get_all_seasons(use_legacy_data=False)
        self.players = self.get_all_players()
        self.dir = dir
        self.src_dir = f'{dir}/src'

        # Read source data from csv
        self.data = self.load_data()

        # Drop unnecessary columns
        print("Processing source data...")
        self.data = self.clean_columns()

        # Aggregate data, by PLAYER_ID
        self.data = self.aggregate_by_player()

        # Combine data from all seasons
        self.df = self.combine_season_data()

        # Sort by PLAYER_ID, SEASON
        self.df = self.df.sort_values(by=['PLAYER_ID', 'SEASON'])

        # Add column about all_nba
        print("Adding all_nba, all_rookie ...")
        self.all_nba_df = self.load_allNBA()
        self.df = self.add_AllNBA()

        # Add column whether player is a rookie
        print("Checking for rookies...")
        self.df = self.add_rookies()

        # Save to csv
        print("Saving data to csv...")
        self.df.to_csv(f'{self.dir}/player_avg_data.csv', index=False, na_rep='None')
        

    def get_all_players(self):
        return nba_api.stats.static.players.get_players()

    # Get all seasons, starting 1946 to current year (based on PC time)
    def get_all_seasons(self, use_legacy_data=True):
        current_year= datetime.now().year
        first_year = 1946 if use_legacy_data else 2012

        seasons = [f'{i}-{str(i+1)[-2:]}' for i in range(first_year, current_year)]
        return seasons
    
    def load_season_data(self, season):
        df = pd.read_csv(f'{self.src_dir}/{season}.csv')
        return df
    
    def load_data(self, load_old=True):
        data = {}
        for season in tqdm(self.seasons, desc="Loading NBA API data from csv", unit="seasons", total=len(self.seasons)):
            df = self.load_season_data(season)
            data[season] = df  

        return data
    
    def clean_columns(self):
        new_data = {}
        for season, df in self.data.items():
            columns_to_drop = [col for col in df.columns if 'RANK' in col]
            columns_to_drop += ['SEASON_YEAR', 'PLAYER_NAME', 'NICKNAME', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP', 'NBA_FANTASY_PTS', 'WNBA_FANTASY_PTS', 'AVAILABLE_FLAG']
    
            new_data[season] = df.drop(columns=columns_to_drop)

        return new_data
    
    # Calculates average data for each player (by aggregating by PLAYER_ID)
    # Based on W/L of the game entry, calculate total games played and win percentage
    def aggregate_by_player(self):
        new_data = {}
        for season, df in self.data.items():
            grouped = df.groupby('PLAYER_ID')

            # Create aggregation dictionary with chosen lambdas for each column
            agg_dict = {col: 'mean' for col in df.columns if col not in ['TEAM_ID', 'PLAYER_ID', 'WL']}
            agg_dict['WL'] = lambda x: x.eq('W').sum()

            # Aggregate
            avg = grouped.agg(agg_dict)
            avg = avg.rename(columns={'WL': 'GW'}) # Games won

            # Calculate Games Played from grouped object size
            avg['GP'] = grouped.size() # Games played

            avg.reset_index(inplace=True)

            new_data[season] = avg

        return new_data
    
    def combine_season_data(self):
        combined_df = pd.concat([df.assign(SEASON=season) for season, df in self.data.items()], ignore_index=True)
        return combined_df
    
    def load_allNBA(self):
        df = pd.read_csv(f'{self.src_dir}/all_nba.csv')
        return df

    def is_AllRookie(self, row):
        player_id = row['PLAYER_ID']
        season = row['SEASON']

        data = self.all_nba_df[(self.all_nba_df['PERSON_ID'] == player_id) & (self.all_nba_df['SEASON'] == season)]
        if data.empty:
            return None
        else:
            data = data.to_dict(orient='records')[0]
            if data['DESCRIPTION'] == "All-Rookie Team":
                return data['ALL_NBA_TEAM_NUMBER']
            else:
                return None

    def is_AllNBA(self, row):
        player_id = row['PLAYER_ID']
        season = row['SEASON']

        data = self.all_nba_df[(self.all_nba_df['PERSON_ID'] == player_id) & (self.all_nba_df['SEASON'] == season)]
        if data.empty:
            return None
        else:
            data = data.to_dict(orient='records')[0]
            if data['DESCRIPTION'] == "All-NBA":
                return data['ALL_NBA_TEAM_NUMBER']
            else:
                return None
    
    def add_AllNBA(self):
        df = self.df.copy()
        df['ALL_ROOKIE_TEAM_NUMBER'] = df.apply(self.is_AllRookie, axis=1)
        df['ALL_NBA_TEAM_NUMBER'] = df.apply(self.is_AllNBA, axis=1)
        return df
    
    # Assume df is sorted by PLAYER_ID, SEASON
    def add_rookies(self):
        df = self.df.copy()
        first_season = df.drop_duplicates(subset='PLAYER_ID', keep='first')

        df['ROOKIE'] = 0

        df.loc[first_season.index, 'ROOKIE'] = 1
        return df

