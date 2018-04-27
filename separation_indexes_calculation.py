import zipfile
import os
from pprint import pprint
import json
import numpy as np

#Script: Processes the timings (json) and calculates indexes for each exercise of a session
#List of exercises: breathing, pvt, signature, transcription, drawing, tma, tmb, tapping, physical

#E4 Files and Sample Rates
ACC = "/ACC.csv"
BVP = "/BVP.csv"
EDA = "/EDA.csv"
HR = "/HR.csv"
IBI = "/IBI.csv"
TAGS = "/tags.csv"
TEMP = "/TEMP.csv"

EXERCISE_LIST = ['breathing', 'pvt', 'signature', 'transcription', 'drawing', 'tma', 'tmb', 'tapping', 'physical']

SAMPLE_RATES = {'ACC': 32, 'BVP': 64, 'EDA': 4, 'TEMP': 4}


def unzip_e4_files(complete_folder):
    for file in os.listdir(complete_folder):
        if file.endswith(".zip"):
            e4_file = file
            print("Found E4 file: " + e4_file)
        elif file.endswith(".json"):
            json_file = file

    if len(os.listdir(complete_folder)) < 3:
        zip = zipfile.ZipFile(complete_folder + "\\" + e4_file, 'r')
        zip.extractall(complete_folder)

    return (e4_file, json_file)

def e4_event_stamp(complete_folder):
    with open(complete_folder + TAGS, 'r') as raw:
        lines = raw.readlines()

    number_lines = len(lines)

    if number_lines == 0:
        print("Warning: E4 event file with 0 events!")
        return None, None

    first_line = lines.pop()
    first_line = first_line.replace('\n', '')
    
    if number_lines == 1:
        return (float(first_line), None)
    elif number_lines == 2:
        second_line = lines.pop()
        second_line = second_line.replace('\n', '')
        return (float(first_line), float(second_line))
    else:
        print("Warning: E4 event file with more than 2 events!")
        return (float(first_line), None)

class timingsParser:
    def __init__(self, json_filename, first_event):
        self.json_filename = json_filename
        self.timings = json.load(open(json_filename, 'r'))
        
        self.computer_epoch = self.timings['epoch_start']
        self.computer_reference = self.timings['experiment_start']
        self.e4_event = first_event
        
        #Contains start and end for each exercise. Measured relative to the variable self.computer_reference
        self.exercise_timings = {}
        self.build_exercise_timings()

        self.sub_exercise_timings = {}
        self.build_sub_exercise_timings()

        #tapping time series + reaction time measures
        self.tapping_total = self.timings['tapping_total']
        self.tapping_array = np.zeros(self.tapping_total)
        self.build_tapping_array()

        self.reaction_array = np.zeros(5)
        self.build_reaction_array()

    def build_exercise_timings(self):
        for exercise in EXERCISE_LIST:
            if exercise == 'drawing': #Because of a bug when generating the JSON input file for activity drawing
                self.exercise_timings[exercise + "_begin"] = self.timings[exercise + "_begin_0"] - self.computer_reference
                self.exercise_timings[exercise + "_end"] = self.timings[exercise + "_end"] - self.computer_reference
            else:
                self.exercise_timings[exercise + "_begin"] = self.timings[exercise + "_begin"] - self.computer_reference
                self.exercise_timings[exercise + "_end"] = self.timings[exercise + "_end"] - self.computer_reference

    def build_sub_exercise_timings(self):
        relevant_exercises = {'pvt': 5, 'signature': 5, 'drawing': 3}

        for exercise in relevant_exercises.keys():
            for i in range(relevant_exercises[exercise]):
                start = exercise + "_begin_" + repr(i)
                finish = exercise + "_end_" + repr(i)
                self.sub_exercise_timings[start] = self.timings[start] - self.computer_reference
                self.sub_exercise_timings[finish] = self.timings[finish] - self.computer_reference
        
        self.sub_exercise_timings['physical_begin_0'] = self.timings["physical_begin"] - self.computer_reference
        self.sub_exercise_timings['physical_end_0'] = self.timings["physical_0"] - self.computer_reference

        self.sub_exercise_timings["physical_begin_1"] = self.timings["physical_0"] - self.computer_reference
        self.sub_exercise_timings["physical_end_1"] = self.timings["physical_1"] - self.computer_reference

        self.sub_exercise_timings["physical_begin_2"] = self.timings["physical_1"] - self.computer_reference
        self.sub_exercise_timings["physical_end_2"] = self.timings["physical_2"] - self.computer_reference

        self.sub_exercise_timings["physical_begin_3"] = self.timings["physical_2"] - self.computer_reference
        self.sub_exercise_timings["physical_end_3"] = self.timings["physical_3"] - self.computer_reference

        self.sub_exercise_timings["physical_begin_4"] = self.timings["physical_3"] - self.computer_reference
        self.sub_exercise_timings["physical_end_4"] = self.timings["physical_4"] - self.computer_reference

        self.sub_exercise_timings["physical_begin_5"] = self.timings["physical_4"] - self.computer_reference
        self.sub_exercise_timings["physical_end_5"] = self.timings["physical_5"] - self.computer_reference

    def build_tapping_array(self):
        for i in range(self.tapping_total):
            self.tapping_array[i] = self.timings["tapping_" + repr(i)] - self.computer_reference

    def build_reaction_array(self):
        for i in range(5):
            self.reaction_array[i] = self.timings["pvt_" + repr(i)]

class exerciseObjects:
    def __init__(self, timings_dictionary):
        print("hello world")


#Define patient and experiment
patient_id = "D1\\"
experiment_number = "1"
base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
complete_folder = base_folder + patient_id + experiment_number

(e4_file, json_file) = unzip_e4_files(complete_folder)

(first_event, second_event) = e4_event_stamp(complete_folder)



timingsObject = timingsParser(complete_folder + "\\" + json_file, first_event)
print("- - - - - - - - - -  - - - - - - - - - - - - - - - - - TIMINGS PRINT - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
pprint(timingsObject.timings)

timingsObject.build_exercise_timings()
timingsObject.build_sub_exercise_timings()