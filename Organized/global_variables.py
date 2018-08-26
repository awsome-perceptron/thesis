import os
import zipfile 

SIGNAL_LIST = ['ACC', 'BVP', 'EDA', 'HR', 'IBI', 'TEMP']
EXERCISE_LIST = ['breathing', 'pvt', 'signature', 'transcription', 'drawing', 'tma', 'tmb', 'tapping', 'physical']
BASE_FOLDER = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
UNITS = {'ACC': "Do this", 'BVP': "Do this", 'EDA': "Do this", 'HR': "Do this", 'IBI': "Do this", 'TEMP': "Do this"}


FEATURES = {"acc": ["mean", "variance", "std", "tv", "energy_bands", "order"]}
FEATURE_TYPES = ["acc"]

RELEVANT_PATIENTS = ["H1", "H2", "H3", "H5", "H6", "H7", "H12", "D1", "D4", "D6"]
RELEVANT_EXPERIMENTS = ["signature", "transcription", "drawing", "tma", "tmb", "physical"]

def get_zip_filename(folder):
    zip_filename = None

    for file in os.listdir(folder):
        if file.endswith(".zip"):
            zip_filename = file

    if zip_filename is None:
        return None

    if len(os.listdir(folder)) < 5: #Usually there are 2 files, but it's possible to have 3 if a correction to the experiment was needed
            zipObj = zipfile.ZipFile(folder + "\\" + zip_filename, 'r')
            zipObj.extractall(folder)
    
    return zip_filename


def get_json_filename(folder):
    for file in os.listdir(folder):
        if file.endswith(".json"):
            if "correcao" not in file and "panas" not in file and "wrong_task" not in file:
                return file
    
    return None