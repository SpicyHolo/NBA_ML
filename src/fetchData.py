from nba_api.stats.endpoints import playergamelogs, playercareerstats, playerawards
import nba_api.stats.static.players

import pandas as pd
import os
import time
from datetime import datetime
from tqdm import tqdm

from csvutils import csvWriter

# Handling writing API data to csv, for faster access

    
# Fetches player data from NBA API to csv by season
class NBAfetchData:
    def __init__(self, dir):
        self.seasons = self.get_all_seasons()
        self.src_dir = f'{dir}/src'

        # Initialise csv files
        self.csv_writer = csvWriter(dir=self.src_dir)

        # Save all season's player data from API to csv 
        self.save_all_seasons()
            
    # Returns list of all players from NBA API
    def get_all_players(self):
        return nba_api.stats.static.players.get_players()

    # Fetches player data from NBA API
    def get_player_stats(self, player_id):
        player = playercareerstats.PlayerCareerStats(player_id=player_id)
        player_stats = player.get_data_frames()[0]
        return player_stats
    
    def get_season_stats(self, season):
        season_data = playergamelogs.PlayerGameLogs(season_nullable=season, season_type_nullable='Regular Season')
        season_df = season_data.get_data_frames()[0]
        return season_df

    def save_season_stats(self, season, df):
        self.csv_writer(season, df)

    # Save all player's data to csv file, by season (usies save_player_stats)
    def save_all_seasons(self):
        n = len(self.seasons)
        for season in tqdm(self.seasons, desc="Fetching NBA API data", unit="seasons", total=n):
            season_stats  = self.get_season_stats(season)
            time.sleep(1)
            self.save_season_stats(season, season_stats)

    # Get all seasons, starting 1946 to current year (based on PC time)
    def get_all_seasons(self):
        current_year= datetime.now().year
        first_year = 1946

        seasons = [f'{i}-{str(i+1)[-2:]}' for i in range(first_year, current_year)]
        return seasons

class AllNBAFetch():
    def __init__(self, dir):
        self.players = self.get_all_players()
        self.dir = dir
        # Fetch reward data for all players
        self.df = self.get_all_players_awards()

        # Save to csv file
        self.df.to_csv(f'{self.dir}/src/all_nba.csv', index=False)
    # Returns list of all players from NBA API
    def get_all_players(self):
        return nba_api.stats.static.players.get_players()


    def get_player_awards(self, player_id):
        player_awards = playerawards.PlayerAwards(player_id=player_id)
        df = player_awards.get_data_frames()[0]
        
        columns_to_drop = [col for col in df.columns.tolist() if col not in ['PERSON_ID', 'DESCRIPTION', 'ALL_NBA_TEAM_NUMBER', 'SEASON']]

        df.drop(columns=columns_to_drop, inplace=True)
        
        mask = df['DESCRIPTION'].isin(['All-NBA', 'All-Rookie Team'])
        df = df[mask] 

        return df

    def get_all_players_awards(self):
        player_data = []
        for player in tqdm(self.players, desc="Fetching ALL_NBA rewards API data", unit="players", total=len(self.players)):
            tmp_df = self.get_player_awards(player['id'])
            if not tmp_df.empty:
                player_data.append(tmp_df)

        df = pd.concat(player_data)

        # Sort by PLAYER_ID, SEASON
        df = df.sort_values(by=['PERSON_ID', 'SEASON'])

        return df