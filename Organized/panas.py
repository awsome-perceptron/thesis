import pandas as pd

class panasParser:
    def __init__(self, complete_folder):
        self.folder = complete_folder
        self.panas_file= self.folder + "\\panas_data.json"
        self.panas_series = pd.read_json(self.panas_file, typ = "series")

class panasFetcher:
    def __init__(self):
        #put things here to fetch google sheets data
        pass