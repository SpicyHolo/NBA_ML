from nba_api.stats.endpoints import playercareerstats

import csv
import os
from datetime import datetime

import nba_api.stats.static.players
from tqdm import tqdm
import pandas as pd

# Handling writing API data to csv, for faster access
class csvWriter():
    def __init__(self, filenames, headers, dir='data/src'):
        self.filenames = filenames
        self.dir = dir

        # Create directory, if doesn't exist
        os.makedirs(self.dir, exist_ok=True)

        # Initialise files for every season with headers
        for filename in filenames:
            with open(self.get_file_path(filename), 'w', newline='') as csv_file:
                csv_handle = csv.writer(csv_file)
                csv_handle.writerow(headers)

        print(f"Initialised csv files in {self.dir}.")

    # Write df (a data row) to given csv file
    def __call__(self, filename, df):
        df.to_csv(self.get_file_path(filename), mode='a', index=False, header=False, na_rep='None')

    # Get csv file path, based on root directory of interface
    def get_file_path(self, filename):
        return f'{self.dir}/{filename}.csv'
    
# Fetches player data from NBA API to csv by season
class NBAfetchData:
    def __init__(self):
        self.players = self.get_all_players()
        self.seasons = self.get_all_seasons()
        
        # Initialise csv files
        self.csv_writer = csvWriter(self.seasons, headers=self.get_headers())

        # Save player's data to csv file, by season
        self.save_all_players_stats()
            
    # Return NBA player stat's df headers
    def get_headers(self):
        id = self.players[0]['id']
        player_stats = self.get_player_stats(id)
        headers = player_stats.columns.tolist()
        return headers
 
    # Returns list of all players from NBA API
    def get_all_players(self):
        return nba_api.stats.static.players.get_players()

    # Fetches player data from NBA API
    def get_player_stats(self, player_id):
        player = playercareerstats.PlayerCareerStats(player_id=player_id)
        player_stats = player.get_data_frames()[0]
        return player_stats

    # Save player's data to csv files, by season
    def save_player_stats(self, player_stats):
        df = player_stats
        for i, row in df.iterrows():
            season_id = row['SEASON_ID']
            row_df = pd.DataFrame(row).T
            self.csv_writer(season_id, row_df)
            
    # Save all player's data to csv file, by season (usies save_player_stats)
    def save_all_players_stats(self):
        total_players = len(self.players)
        for player in tqdm(self.players, desc="Fetching NBA API data", unit="players", total=total_players):
            id = player['id']
            player_stats = self.get_player_stats(id)
            self.save_player_stats(player_stats)

    # Get all seasons, starting 1946 to current year (based on PC time)
    def get_all_seasons(self):
        current_year= datetime.now().year
        first_year = 1946

        seasons = [f'{i}-{str(i+1)[-2:]}' for i in range(first_year, current_year)]
        return seasons

