import os
import zipfile 

SIGNAL_LIST = ['ACC', 'BVP', 'EDA', 'HR', 'IBI', 'TEMP']
EXERCISE_LIST = ['breathing', 'pvt', 'signature', 'transcription', 'drawing', 'tma', 'tmb', 'tapping', 'physical']


def get_zip_filename(folder):
    zip_filename = None

    for file in os.listdir(folder):
        if file.endswith(".zip"):
            zip_filename = file

    if zip_filename is None:
        print("Error on finding zip file")
        return None

    if len(os.listdir(folder)) < 4: #Usually there are 2 files, but it's possible to have 3 if a correction to the experiment was needed
            zipObj = zipfile.ZipFile(folder + "\\" + zip_filename, 'r')
            zipObj.extractall(folder)
    
    return zip_filename


def get_json_filename(folder):
  
    for file in os.listdir(folder):
        if file.endswith(".json"):
            if "correcao" not in file and "panas" not in file:
                return file
    
    return None