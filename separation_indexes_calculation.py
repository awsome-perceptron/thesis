import zipfile
import os
from pprint import pprint
import json
import numpy as np
import pandas as pd
from math import ceil

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

SESSION_FILES = ["ACC.csv", "BVP.csv", "EDA.csv", "HR.csv", "IBI.csv", "TEMP.csv"]

EXERCISE_LIST = ['breathing', 'pvt', 'signature', 'transcription', 'drawing', 'tma', 'tmb', 'tapping', 'physical']
SIGNAL_LIST = ['ACC', 'BVP', 'EDA', 'HR', 'IBI', 'TEMP'] #IBI is odd

SAMPLE_RATES = {'ACC': 32, 'BVP': 64, 'EDA': 4, 'TEMP': 4, 'HR': 1}

def unzip_e4_files(complete_folder):
    #SHOULD NOT BE USED
    e4_file = None
    json_file = None

    for file in os.listdir(complete_folder):
        if file.endswith(".zip"):
            e4_file = file
        elif file.endswith(".json"):
            json_file = file

    if e4_file == None or json_file == None:
        print("Error: E4 file or JSON file not found")
        print("Check folder: " + complete_folder)
        
    if len(os.listdir(complete_folder)) < 4: #Usually there are 2 files, but it's possible to have 3 if a correction to the experiment was needed
        zip = zipfile.ZipFile(complete_folder + "\\" + e4_file, 'r')
        zip.extractall(complete_folder)

    return (e4_file, json_file)

def get_files_name(experiment_folder):
        (e4_file, json_file) = (None, None)

        for file in os.listdir(experiment_folder):
            if file.endswith(".zip"):
                e4_file = file
            elif file.endswith(".json"):
                if "correcao" not in file:
                    json_file = file

        if e4_file == None or json_file == None:
            print("Error: There is no E4 or JSON file for patient " + self.patient_id + " in experiment " + repr(self.experiment_number))
            return (None, None)
            
        if len(os.listdir(experiment_folder)) < 4: #Usually there are 2 files, but it's possible to have 3 if a correction to the experiment was needed
            zip = zipfile.ZipFile(experiment_folder + "\\" + e4_file, 'r')
            zip.extractall(experiment_folder)

        return (e4_file, json_file)
        
class timingsParser:
    def __init__(self, complete_folder, json_filename, empaticaObject):
        self.json_file = complete_folder + "\\" + json_filename
        self.complete_folder = complete_folder
        self.timings = json.load(open(self.json_file, 'r'))
        
        self.computer_epoch = self.timings['epoch_start']
        self.computer_reference = self.timings['experiment_start']
        self.experiment_timestamp = self.timings['timestamp_start']

        self.e4_event_epoch = empaticaObject.first_event
        self.e4_signal_stamps = empaticaObject.e4_signal_stamps
        self.e4_signal_rates = empaticaObject.e4_signal_rates
        
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
        self.reaction_errors = self.timings['pvt_errors']
        self.build_reaction_array()

        #Contains start and end index for each exercise. Considers only the total duration of the exercise
        self.exercise_indexes = {}
        self.sub_exercise_indexes = {}

        self.calculate_indexes(self.exercise_timings, self.exercise_indexes)
        self.calculate_indexes(self.sub_exercise_timings, self.sub_exercise_indexes)

    def build_exercise_timings(self):
        for exercise in EXERCISE_LIST:
            self.exercise_timings[exercise] = {}
            if exercise == 'drawing': #Because of a bug when generating the JSON input file for activity drawing
                self.exercise_timings[exercise]['begin'] = self.timings[exercise + "_begin_0"] - self.computer_reference
                self.exercise_timings[exercise]['end'] = self.timings[exercise + "_end"] - self.computer_reference
            else:
                self.exercise_timings[exercise]['begin'] = self.timings[exercise + "_begin"] - self.computer_reference
                self.exercise_timings[exercise]['end'] = self.timings[exercise + "_end"] - self.computer_reference

    def build_sub_exercise_timings(self):
        relevant_exercises = {'pvt': 5, 'signature': 5, 'drawing': 3}

        for exercise in relevant_exercises.keys():
            for i in range(relevant_exercises[exercise]):
                sub_exercise_key = exercise + "_" + repr(i)
                start = exercise + "_begin_" + repr(i)
                finish = exercise + "_end_" + repr(i)

                self.sub_exercise_timings[sub_exercise_key] = {}
                self.sub_exercise_timings[sub_exercise_key]['begin'] = self.timings[start] - self.computer_reference
                self.sub_exercise_timings[sub_exercise_key]['end'] = self.timings[finish] - self.computer_reference
        
        self.sub_exercise_timings['physical_0'] = {}
        self.sub_exercise_timings['physical_0']['begin'] = self.timings["physical_begin"] - self.computer_reference
        self.sub_exercise_timings['physical_0']['end'] = self.timings["physical_0"] - self.computer_reference

        self.sub_exercise_timings['physical_1'] = {}
        self.sub_exercise_timings['physical_1']['begin'] = self.timings["physical_0"] - self.computer_reference
        self.sub_exercise_timings['physical_1']['end'] = self.timings["physical_1"] - self.computer_reference

        self.sub_exercise_timings['physical_2'] = {}
        self.sub_exercise_timings['physical_2']['begin'] = self.timings["physical_1"] - self.computer_reference
        self.sub_exercise_timings['physical_2']['end'] = self.timings["physical_2"] - self.computer_reference

        self.sub_exercise_timings['physical_3'] = {}
        self.sub_exercise_timings['physical_3']['begin'] = self.timings["physical_2"] - self.computer_reference
        self.sub_exercise_timings['physical_3']['end'] = self.timings["physical_3"] - self.computer_reference

        self.sub_exercise_timings['physical_4'] = {}
        self.sub_exercise_timings['physical_4']['begin'] = self.timings["physical_3"] - self.computer_reference
        self.sub_exercise_timings['physical_4']['end'] = self.timings["physical_4"] - self.computer_reference

        self.sub_exercise_timings['physical_5'] = {}
        self.sub_exercise_timings['physical_5']['begin'] = self.timings["physical_4"] - self.computer_reference
        self.sub_exercise_timings['physical_5']['end'] = self.timings["physical_5"] - self.computer_reference

    def build_tapping_array(self):
        for i in range(self.tapping_total):
            self.tapping_array[i] = self.timings["tapping_" + repr(i)] - self.computer_reference

    def build_reaction_array(self):
        for i in range(5):
            self.reaction_array[i] = self.timings["pvt_" + repr(i)]

    def calculate_indexes(self, input_dictionary, output_dictionary):
        for item in input_dictionary:
            output_dictionary[item] = {}
            self.calculate_exercise_indexes(item, input_dictionary[item]['begin'], input_dictionary[item]['end'], output_dictionary[item])

    def calculate_exercise_indexes(self, exercise, begin_time, end_time, output_dictionary):
        for signal in SIGNAL_LIST:
            if signal == "IBI":
                continue
            else:
                (start_index, end_index) = self.calculate_signal_indexes(signal, begin_time, end_time)
                output_dictionary[signal] = {}
                output_dictionary[signal]['start_index'] = ceil(start_index)
                output_dictionary[signal]['end_index'] = ceil(end_index)
    
    def calculate_signal_indexes(self, signal_type, begin_time, end_time):
        e4_offset = self.e4_event_epoch - self.e4_signal_stamps[signal_type]
        #MORE PRECISION: CONSIDER ERROR BETWEEN EPOCHS FROM E4 AND COMPUTER
        
        start_index = SAMPLE_RATES[signal_type] * (e4_offset + begin_time)
        end_index = SAMPLE_RATES[signal_type] * (e4_offset + end_time)

        return (start_index, end_index)

class empaticaParser:
    def __init__(self, complete_folder, e4_filename):
        self.complete_folder = complete_folder
        self.e4_file = complete_folder + "\\" + e4_filename

        (self.first_event, self.second_event) = self.parse_events_file()

        #open session files and extract timestamps, sample rates and data
        self.e4_signal_stamps = {}
        self.e4_signal_rates = {}

        self.parse_stamp_and_rate()

        self.acc = self.parse_file("ACC", 3, ['X', 'Y', 'Z'])
        self.bvp = self.parse_file("BVP", 1)
        self.eda = self.parse_file("EDA", 1)
        self.hr = self.parse_file("HR", 1)
        self.temp = self.parse_file("TEMP", 1)
        self.ibi = self.parse_file("IBI", 2, ['t', 'd'])

        self.data = {'ACC': self.acc, 'BVP':  self.bvp, 'EDA': self.eda, 'HR': self.hr, 'TEMP': self.temp, 'IBI': self.ibi}

    def parse_events_file(self):
        with open(self.complete_folder + TAGS, 'r') as raw:
            lines = raw.readlines()

        number_lines = len(lines)

        if number_lines == 0:
            print("Warning: E4 event file with 0 events!")
            return None, None

        first_line = lines.pop(0)
        first_line = first_line.replace('\n', '')
        
        if number_lines == 1:
            return (float(first_line), None)
        elif number_lines == 2:
            second_line = lines.pop(0)
            second_line = second_line.replace('\n', '')
            return (float(first_line), float(second_line))
        else:
            print("Warning: E4 event file with more than 2 events!")
            return (float(first_line), None)

    def parse_stamp_and_rate(self):
        for signal in SIGNAL_LIST:
            with open(self.complete_folder + "\\" + signal + ".csv", 'r') as f:
                first_line = f.readline()
                second_line = f.readline()
            
            first_line = first_line.replace('\n', '')
            first_line = first_line.split(',')
            second_line = second_line.replace('\n', '')
            second_line = second_line.split(',')
            
            if signal == "ACC":
                x_timestamp = float(first_line[0])
                y_timestamp = float(first_line[1])
                z_timestamp = float(first_line[2])

                x_samplerate = float(second_line[0])
                y_samplerate = float(second_line[1])
                z_samplerate = float(second_line[2])

                #verify if timestamp is equal for all axis
                if x_timestamp == y_timestamp == z_timestamp:
                    self.e4_signal_stamps[signal] = x_timestamp
                else:
                    print("WARNING: Actigraphy timestamps are different according to the axis!")

                #verify is sample rate is equal for all axis
                if x_samplerate == y_samplerate == z_samplerate:
                    self.e4_signal_rates[signal] = x_samplerate
                else:
                    print("WARNING: Actigraphy sample rate is different according to the axis!")
            
            else:
                #Store timestamp
                self.e4_signal_stamps[signal] = float(first_line[0])
                
                #IBI signal has no sample rate
                if(signal == "IBI"):
                    continue
                else:
                    self.e4_signal_rates[signal] = float(second_line[0])

    def parse_data(self):
        dictionary = {}
        for signal in SIGNAL_LIST:
            if signal == "ACC":
                dictionary[signal] = self.parse_file(signal, 3, ['X', 'Y', 'Z'])
            elif signal == "IBI":
                dictionary[signal] = self.parse_file(signal, 2, ['t', 'd'])
            else:
                dictionary[signal] = self.parse_file(signal, 1)

        return dictionary

    def parse_file(self, signal, number_columns, cols = None):
        with open(self.complete_folder + "\\" + signal + ".csv", 'r') as raw:
            lines = raw.readlines()
        
        discard = lines.pop(0) #discard first line

        if signal != "IBI":
            discard = lines.pop(0) #discard second line

        data_as_float = np.zeros((len(lines), number_columns), dtype = float)

        for i in range(len(lines)):
            lines[i] = lines[i].replace('\n', '')
            lines[i] = lines[i].split(',')
            data_as_float[i] = np.asarray(lines[i], dtype = float)

        return pd.DataFrame(data_as_float, columns = cols)
    
if __name__ == "__main__":
    patient_id = "D1\\"
    experiment_number = "1"
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient_id + experiment_number

    (e4_file, json_file) = get_files_name(complete_folder)

    empaticaObject = empaticaParser(complete_folder, e4_file)

    timingsObject = timingsParser(complete_folder, json_file, empaticaObject)

