from fetch import NBAfetchData, AllNBAFetch

from processData import processData
import os
import pandas as pd
def main():
    dir = 'data'    

    # Check for source data
    if not(os.path.exists(dir)):
        fetch_data = NBAfetchData(dir=dir)

    print(f'Found source NBA data in {dir}')

    # process_data = processData(dir)
    fetch_all_nba = AllNBAFetch(dir=dir)
    
    

if __name__ == "__main__":
    main()