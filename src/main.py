from fetchData import NBAfetchData, AllNBAFetch

from processData import processData
from model import modelNBA
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
    nba_model = modelNBA(df)
    print("Training model")
    nba_model.train()

if __name__ == "__main__":
    main()