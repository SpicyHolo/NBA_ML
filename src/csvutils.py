import os

class csvWriter():
    def __init__(self, dir='data/src'):
        self.dir = dir

        # Create directory, if doesn't exist
        os.makedirs(self.dir, exist_ok=True)
        print(f"Initialised data dir {self.dir}.")

    # Write df (a data row) to given csv file
    def __call__(self, filename, df):
        file_path = self.get_file_path(filename)

        # Add headers, if the file doesn't exist yet.
        if not(os.path.isfile(file_path)):
            df.to_csv(file_path, mode='a', index=False, header=True, na_rep='None')
        else:
            df.to_csv(file_path, mode='a', index=False, header=False, na_rep='None')

    # Get csv file path, based on root directory of interface
    def get_file_path(self, filename):
        return f'{self.dir}/{filename}.csv'