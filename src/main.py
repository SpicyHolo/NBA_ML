from fetchData import NBAfetchData, AllNBAFetch

from processData import processData
from model import modelNBA
from csvutils import resultWriter 

import os
import pandas as pd
def main():
    dir = 'data'    


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
    nba_model = modelNBA(df, rookie=False, exclude_rookies=True)
    rookie_model = modelNBA(df, rookie=True)

    print("Training model")
    nba_model.train()
    rookie_model.train()

    all_nba_players = nba_model.predict('2023', player_num=15)
    rookie_players = rookie_model.predict('2023', player_num=10)
    
    print(all_nba_players[['NAME', 'ALL_NBA_PROB']])
    print(rookie_players[['NAME', 'ALL_NBA_PROB']])
    all_nba = all_nba_players[['NAME']].values.tolist()
    all_nba =[x[0] for x in all_nba]

    rookie = rookie_players[['NAME']].values.tolist()
    rookie = [x[0] for x in rookie]

    # Prepare output dictionary
    result_dict = {'first all-nba team': all_nba[:5], 
                   'second all-nba team': all_nba[5:10], 
                   'third all-nba team': all_nba[10:15],
                   'first rookie all-nba team': rookie[:5],
                   'second rookie all-nba team': rookie[5:10]}

    result_writer = resultWriter(dir='data/out')
    result_writer('result.json', result_dict)
    
if __name__ == "__main__":
    main()