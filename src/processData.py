from datetime import datetime
import pandas as pd
from tqdm import tqdm

class processData:
    def __init__(self, dir):
        self.seasons = self.get_all_seasons()
        self.dir = dir
        self.src_dir = f'{dir}/src'

        # Read source data from csv
        self.data = self.load_data(load_old=False)

        # Drop unnecessary columns
        self.data = self.clean_columns()

        # Aggregate data, by PLAYER_ID
        self.data = self.aggregate_by_player()

        # Combine data from all seasons
        self.df = self.combine_season_data()

        # Save to csv
        self.df.to_csv(f'{self.dir}/player_avg_data.csv', index=False)


    # Get all seasons, starting 1946 to current year (based on PC time)
    def get_all_seasons(self):
        current_year= datetime.now().year
        first_year = 1946

        seasons = [f'{i}-{str(i+1)[-2:]}' for i in range(first_year, current_year)]
        return seasons
    
    def load_season_data(self, season):
        df = pd.read_csv(f'{self.src_dir}/{season}.csv')
        return df
    
    def load_data(self, load_old=True):
        data = {}
        for season in tqdm(self.seasons, desc="Loading NBA API data from csv", unit="seasons", total=len(self.seasons)):
            if self.isOld(season) and load_old == False:
                continue
            df = self.load_season_data(season)
            data[season] = df  

        return data
    
    # Checks if chosen season has old data format (which has different fields)
    def isOld(self, season):
        start, _ = map(int, season.split('-'))
        return start < 1996

    def clean_columns(self):
        new_data = {}
        for season, df in tqdm(self.data.items(), desc="Cleaning data...", unit="seasons", total=len(self.data)):
            columns_to_drop = [col for col in df.columns if 'RANK' in col]
            columns_to_drop += ['SEASON_YEAR', 'PLAYER_NAME', 'NICKNAME', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'GAME_ID', 'GAME_DATE', 'MATCHUP', 'NBA_FANTASY_PTS', 'WNBA_FANTASY_PTS', 'AVAILABLE_FLAG']
    
            new_data[season] = df.drop(columns=columns_to_drop)

        return new_data
    
    # Calculates average data for each player (by aggregating by PLAYER_ID)
    # Based on W/L of the game entry, calculate total games played and win percentage
    def aggregate_by_player(self):
        new_data = {}
        for season, df in tqdm(self.data.items(), desc="Calculating averages...", unit="seasons", total=len(self.data)):
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
        combined_df = pd.concat([df.assign(SEASON=season) for season, df in tqdm(self.data.items(), desc="Combining data...", unit="seasons", total=len(self.data))], ignore_index=True)
        return combined_df
    
