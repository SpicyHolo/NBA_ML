from src.fetchData import NBAfetchData, AllNBAFetch
from src.processData import processData
from src.model import modelNBA


import os
import argparse
import json
import pandas as pd

def getAllNba(df, rookies):
    nba_model = modelNBA(df, rookies)
    
    # Using ridge regressor for top 5 players, and LogisticRegression for the rest
    nba_model2 = modelNBA(df, rookies, use_ridge=True)

    nba_model.train()
    nba_model2.train()

    num_of_players = 10 if rookies else 15
    all_nba  = nba_model.predict('2023', player_num=num_of_players)
    all_nba2 = nba_model2.predict('2023', player_num=5)
    all_nba = all_nba[['NAME']].values.tolist()
    all_nba =[x[0] for x in all_nba]

    all_nba2 = all_nba2[['NAME']].values.tolist()
    all_nba2 =[x[0] for x in all_nba2]

    return all_nba2 + all_nba[5:]

def main():
    parser = argparse.ArgumentParser(description='Write text to a file.')
    parser.add_argument('output_file', type=str, help='Output file name')
    args = parser.parse_args()
    dir = 'data'    
    output_file = args.output_file

    # Check for source data
    if not(os.path.exists(dir)):
        fetch_data = NBAfetchData(dir=dir)
        fetch_all_nba = AllNBAFetch(dir=dir)
    print(f'Found source NBA data in {dir}')

    # Check for processedData
    if not(os.path.isfile(f'{dir}/player_avg_data.csv')):
        process_data = processData(dir=dir)
    print(f"Found processed data in {dir}/player_avg_data.csv")

    # Load data
    df = pd.read_csv(f'{dir}/player_avg_data.csv')

    # Actual Machine Learning starts here...
    all_nba = getAllNba(df, rookies=False)
    rookies = getAllNba(df, rookies=True)

    # Prepare output dictionary
    result_dict = {'first all-nba team': all_nba[:5], 
                   'second all-nba team': all_nba[5:10], 
                   'third all-nba team': all_nba[10:15],
                   'first rookie all-nba team': rookies[:5],
                   'second rookie all-nba team': rookies[5:10]}

    with open(output_file, 'w') as json_file:
        json.dump(result_dict, json_file, indent=2)

    
if __name__ == "__main__":
    main()