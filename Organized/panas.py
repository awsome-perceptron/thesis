import pandas as pd
import global_variables as gv


class panasParser:
    def __init__(self, complete_folder):
        self.folder = complete_folder
        self.panas_file= self.folder + "\\panas_data.json"
        self.panas_series = pd.read_json(self.panas_file, typ = "series")


if __name__ == "__main__":
    patient_id = "H1"
    experiment_number = 3
    folder = gv.BASE_FOLDER + patient_id + "//" + repr(experiment_number)
    panasObject = panasParser(folder)
