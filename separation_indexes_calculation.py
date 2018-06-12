import zipfile
import os
from pprint import pprint
import json
import numpy as np
import pandas as pd
from math import ceil
import datetime
import time
import sys
import matplotlib.pyplot as plt
import copy

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

RELEVANT_SIGNALS = {"breathing": ["BVP",], "pvt": ["HR",], "signature": ["ACC",], "transcription": ["ACC",], "drawing": ["ACC",], "tma": ["ACC",], "tmb": ["ACC",],  "tapping": ["HR",], "physical": ["ACC",]}

BASE_FOLDER =  "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"

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
                if "correcao" not in file and "panas" not in file:
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
        self.exercise_timings = self.build_exercise_timings()
        self.exercise_duration = self.build_exercises_duration()

        self.sub_exercise_timings = {}
        self.build_sub_exercise_timings()
        #self.sub_exercise_duration = self.build_sub_exercise_duration() DEVELOP THIS LATER

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
        timings_dictionary = {}
        for exercise in EXERCISE_LIST:
            timings_dictionary[exercise] = {}
            if exercise == 'drawing': #Because of a bug when generating the JSON input file for activity drawing
                timings_dictionary[exercise]['begin'] = self.timings[exercise + "_begin_0"] - self.computer_reference
                timings_dictionary[exercise]['end'] = self.timings[exercise + "_end"] - self.computer_reference
            else:
                timings_dictionary[exercise]['begin'] = self.timings[exercise + "_begin"] - self.computer_reference
                timings_dictionary[exercise]['end'] = self.timings[exercise + "_end"] - self.computer_reference

        return timings_dictionary

    def build_exercises_duration(self):
        duration_dictionary = {}
        for exercise in EXERCISE_LIST:
            duration_dictionary[exercise] = self.exercise_timings[exercise]["end"] - self.exercise_timings[exercise]["begin"]
        
        return duration_dictionary
    
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
        
        self.actigraphy_detrended = self.data["ACC"].copy(deep = True)
        self.data_detrended = {'ACC': self.actigraphy_detrended, 'BVP':  self.bvp, 'EDA': self.eda, 'HR': self.hr, 'TEMP': self.temp, 'IBI': self.ibi}

        #Will be filled when method for detrend is called
        self.actigraphy_means = {}

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
   
    def actigraphy_task_detrend(self, task_name, start_index, end_index):
        mean_vector = np.zeros(3)

        start_index = start_index
        end_index = end_index

        if start_index > len(self.actigraphy_detrended) or end_index > len(self.actigraphy_detrended):
            raise dataSlicingException("Indexes bigger than original data", task_name, "ACC", start_index, end_index, "Size: " + repr(len(self.actigraphy_detrended)))
                    
        data_slice = self.actigraphy_detrended[start_index:end_index]
        length = len(data_slice)
        
        for i, axis in enumerate(self.actigraphy_detrended):
            mean_vector[i] = data_slice[axis].sum()/length
            self.actigraphy_means[task_name] = mean_vector
            self.actigraphy_detrended[axis][start_index:end_index] = self.actigraphy_detrended[axis][start_index:end_index] - mean_vector[i]

    def build_actigraphy_magnitude(self):
        data = self.actigraphy_detrended
        self.actigraphy_magnitude = np.sqrt(data['X']**2 + data['Y']**2 + data['Z']**2)
    

class panasParser:
    def __init__(self, complete_folder):
        self.folder = complete_folder
        self.panas_file= self.folder + "\\panas_data.json"
        self.panas_series = pd.read_json(self.panas_file, typ = "series")

class completeSession:
    def __init__(self, empaticaObj, timingsObj, panasObj):
        self.empaticaObject = empaticaObj
        self.timingsObject = timingsObj
        self.panasObject = panasObj

        self.existing_tasks = []

        self.detrend_actigraphy(self.timingsObject.exercise_indexes, "task_detrend")
        self.pauses_indexes = self.between_tasks()
        self.detrend_actigraphy(self.pauses_indexes, "not_task_detrend")

        self.empaticaObject.build_actigraphy_magnitude()
        self.tasks_features_dictionary = self.build_feature_objects()

    def detrend_actigraphy(self, input_dictionary, mode):
        #if mode == task_detrend -> store mean_array
        means_dictionary = {}

        for task in input_dictionary.keys():
            task_indexes = input_dictionary[task]
            try:
                start_index = task_indexes["ACC"]["start_index"]
                end_index = task_indexes["ACC"]["end_index"]
                #print("----------------------------")
                #print("\n Before Detrending: {}".format(self.empaticaObject.actigraphy_detrended[start_index:end_index].head(3)))

                mean_array = self.empaticaObject.actigraphy_task_detrend(task, start_index, end_index)
                #print("Task: {} - Mean Array: {}".format(task, mean_array))

                #print("After Detrending: {}".format(self.empaticaObject.actigraphy_detrended[start_index:end_index].head(3)))

                if mode == "task_detrend":
                    self.existing_tasks.append(task)
                
            except dataSlicingException as d:
                #missing some data
                print("WARNING - MISSING SOME DATA")
                print(d.args)
            except:
                #unknown errors
                print("Unexpected error:", sys.exc_info()[0])
                raise
    
    def between_tasks(self):
        #generate dictionary, call empatica method
        new_dictionary = {}

        #deep copy of empatica's dictionary
        exercise_indexes = copy.deepcopy(self.timingsObject.exercise_indexes)

        #Setup in the beggining
        old_task = "beggining"
        exercise_indexes[old_task] = {}
        exercise_indexes[old_task]["ACC"] = {}
        exercise_indexes[old_task]["ACC"]["end_index"] = 0  
        
        for task in self.timingsObject.exercise_indexes.keys():
            key = old_task + "_" + task
            new_dictionary[key] = {}
            new_dictionary[key]["ACC"] = {'start_index': exercise_indexes[old_task]["ACC"]["end_index"], 'end_index': exercise_indexes[task]["ACC"]["start_index"]}
            old_task = task

        #Setup in the end
        new_dictionary["physical_end"] = {}
        new_dictionary["physical_end"]["ACC"] = {"start_index": exercise_indexes["physical"]["ACC"]["end_index"], "end_index": len(self.empaticaObject.actigraphy_detrended)}
    

        return new_dictionary

    def build_feature_objects(self):
        feature_objects_dictionary = {}
        for task in self.existing_tasks:
            timings = self.timingsObject.exercise_timings[task]
            indexes = self.timingsObject.exercise_indexes[task]
            acc_start_index = indexes["ACC"]["start_index"]
            acc_end_index = indexes["ACC"]["end_index"]

            task_actigraphy_detrended = self.empaticaObject.data_detrended["ACC"][acc_start_index:acc_end_index]
            duration = self.timingsObject.exercise_duration[task]

            feature_objects_dictionary[task] = taskFeatures(task, timings, indexes, duration, task_actigraphy_detrended, self.empaticaObject.actigraphy_means[task])
        
        return feature_objects_dictionary


class taskFeatures:
    def __init__(self, task_name, task_timings, signals_indexes, duration, task_actigraphy_detrended, mean_actigraphy):
        #Note: task_data is not being used right not now, but could be added to this class constructor, if necessary
        self.task_name = task_name
        self.timings = task_timings
        self.signal_indexes = signals_indexes
        self.duration = duration
        
        self.actigraphy_features = actigraphyFeatures(task_actigraphy_detrended, mean_actigraphy)


class actigraphyFeatures:
    def __init__(self, task_actigraphy_detrended, task_mean_actigraphy):
        self.acc_detrended = task_actigraphy_detrended
        self.actigraphy_magnitude = self.calculate_magnitude()

        #self.mean_array = task_mean_actigraphy
        #self.mean = self.mean()

        #self.variance = self.sample_variance()
        #self.standard_deviation = self.standard_deviation()
        
        #self.feature_description = self.build_feature_description()
    
    def calculate_magnitude(self):
        return np.sqrt(self.acc_detrended['X']**2 + self.acc_detrended['Y']**2 + self.acc_detrended['Z']**2)
    
    def mean(self):
        #Almost all means are equal
        return np.sqrt(np.sum(np.square(self.mean_array)))/3

    def sample_variance(self):

        #return np.sum(self.actigraphy_magnitude
        pass    
    
    def standard_deviation(self):
        return np.sqrt(self.sample_variance)

    def build_feature_description(self):
        description = {}
        
        #Mean
        description['mean'] = {'X': self.mean_array[0], 'Y': self.mean_array[1], 'Z': self.mean_array[0]}

        return description
    
    def print_feature_description(self, task_name):
        print(" --- Actigraphy Feature Description - Task: ", task_name)
        for key in self.feature_description.keys():
            if type(self.feature_description[key]) is dict:
                print("-> Listing features related to {}".format(key))
                for name in self.feature_description[key]:
                    print("     {} : {}".format(name, self.feature_description[key][name]))

            else:
                print("{} : {}".format(key, self.feature_description[key]))
        

class unitTesting:
    def __init__(self, sessionObject):
        self.sessionObject = sessionObject
    
    def detrended_actigraphy(self):
        print("-------------------------  UNIT TESTING: Actigraphy Detrended Signal  -----------------------")
        
        original = self.sessionObject.empaticaObject.data["ACC"]
        detrended = self.sessionObject.empaticaObject.data_detrended["ACC"]

        counter = 0
        ini_time = time.perf_counter()

        for i in range(len(original)):
            for axis in detrended:
                if detrended[axis][i] != original[axis][i]:
                    counter = counter + 1
        
        end_time = time.perf_counter()

        print("Actigraphy detrending - Time to run: ", end_time - ini_time)
        print("Original and detrended signal have ", counter, " different points!")

    def actigraphy_means_dictionary(self):
        print("-------------------------  UNIT TESTING: Actigraphy Means Dictionary  -----------------------")

        dic = self.sessionObject.actigraphy_means

        for task in dic.keys():
            print("Task name: ", task, " - (ux, uy, uz) = (", dic[task][0], ",", dic[task][1], ",", dic[task][2], ")")
    
    def between_tasks_dictionary(self):
        dictionary = self.sessionObject.pauses_indexes
        exercise_indexes = self.sessionObject.timingsObject.exercise_indexes

        print("\n Unit testing: between_tasks_dictionary()")

        print(" -------------------- Original Tasks Indexes ---------------------- ")

        for task in exercise_indexes.keys():
            print("[ACC] - Task: {} - Start: {} - End: {}".format(task, exercise_indexes[task]["ACC"]["start_index"], exercise_indexes[task]["ACC"]["end_index"]))

        print(" ------------------- Between Tasks Indexes ----------------------- ")
        for key in dictionary.keys():
            print("[ACC] - Key: {} - Start: {} - End: {}".format(key, dictionary[key]["ACC"]["start_index"], dictionary[key]["ACC"]["end_index"]))

        print("\n")
        
    def detrended_actigraphy_means(self, exercise_indexes, pauses_indexes):
        mean_array = np.zeros(3)
        print("\n Unit testing: detrended_actigraphy_means(exercise_indexes, pause_indexes) -> should be approximately 0")

        print(" ------------------- Average inside Tasks ---------------------- ")

        for task in exercise_indexes.keys():
            start = exercise_indexes[task]["ACC"]["start_index"]
            end = exercise_indexes[task]["ACC"]["end_index"]
            data = self.sessionObject.empaticaObject.actigraphy_detrended[start:end]
            length = len(data)

            for i, axis in enumerate(data):
                mean_array[i] = data[axis].sum()/length

            print("Task: {} - Mean Array: ({},{},{})".format(task, mean_array[0], mean_array[1], mean_array[2]))

        print(" ----------------------- Average Inside Pauses -------------------- ")
        
        for task in pauses_indexes.keys():
            start = pauses_indexes[task]["ACC"]["start_index"]
            end = pauses_indexes[task]["ACC"]["end_index"]
            data = self.sessionObject.empaticaObject.actigraphy_detrended[start:end]
            length = len(data)

            for i, axis in enumerate(data):
                mean_array[i] = data[axis].sum()/length

            print("Task: {} - Mean Array: ({},{},{})".format(task, mean_array[0], mean_array[1], mean_array[2]))


#GENERAL METHODS TO BE DEVELOPED YET
def matplot_experiment(patient_id, experiment_number, view_mode):

    print("Write code to plot one experiment")

def matplot_all_experiments(patient_id, view_mode):
    
    print("Write code to plot all experiments")

def display_by_tasks(patient_id, experiment_number):

    print("Write code to display by tasks")
    
def display_by_raw_signals(patient_id, experiment_number):

    print("Write code to display by raw signals")

class dataSlicingException(Exception):
    #User defined Exception class
    def __init__(self, message, exercise, signal, start_index, end_index, length):
        self.message = message
        self.exercise = exercise
        self.signal = signal
        self.start_index = start_index
        self.end_index = end_index
        self.length = length


if __name__ == "__main__":
    patient_id = "D1\\"
    experiment_number = "3"
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient_id + experiment_number

    (e4_file, json_file) = get_files_name(complete_folder)

    empaticaObject = empaticaParser(complete_folder, e4_file)

    timingsObject = timingsParser(complete_folder, json_file, empaticaObject)

    panasObject = panasParser(complete_folder)

    sessionObject = completeSession(empaticaObject, timingsObject, panasObject)

    unitTests = unitTesting(sessionObject)
    #unitTests.between_tasks_dictionary()
    #unitTests.detrended_actigraphy_means(timingsObject.exercise_indexes, sessionObject.pauses_indexes)
  
    # print("Actigraphy magnitude")
    # print(empaticaObject.actigraphy_magnitude)
    # plt.figure()
    # plt.plot(empaticaObject.actigraphy_magnitude)
    # plt.show()
    plt.figure()
    plt.plot(empaticaObject.actigraphy_magnitude)
    plt.show()

    #Iterate through patient