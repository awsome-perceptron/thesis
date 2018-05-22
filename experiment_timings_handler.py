import sqlite3
import json
from pprint import pprint
from math import ceil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#python script:
#input: a timings.json file + an e4 session data
#responsible for: 1) associates the timings.json to the e4 session data. Moves the files to the patient folder.
#                 2) processes the json file to calculate the respective indexes that separate the data according to the part of the experiment
#Note: the different experiment parts are: breathing, reaction_time, signature, tma, tmb and physical

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
class syncObject:
    #class variables
    #SAMPLE_RATES = {'ACT': 32, 'BVP': 64, 'EDA': 4, 'TEMP': 4} #NEED TO ADD IBI AND HR, BUT FIRST NEED TO UNDERSTAND IT BETTER

    def __init__(self, input_json, e4_time_dic, e4_sample_dic, e4_events_dic):
        self.json_filename = input_json
        
        self.time_measures = json.load(open(self.json_filename))
        self.computer_timestamp = self.time_measures['timestamp']
        self.computer_reference = self.time_measures['t1']
        self.computer_epoch = self.time_measures['epoch']

        #store e4 timestamps and sample rates
        self.e4_timestamps = e4_time_dic
        self.e4_sample_rates = e4_sample_dic
        self.e4_events = e4_events_dic

        #stores begin and end time for each experiment (relative to the computer)
        self.experiments_timings = {}

        #stores begin and end index for each experiment for every data type
        self.experiments_indexes = {}
        
        #Process input json, containing time measures acquired from the computer. Builds structure with begin and end time for each activity
        self.insert_relative_timings()
        self.insert_reaction_times()
        
        #verify and process actigraphy timestamps and samplerates
        self.process_ACT_timestamp_sample_rate()

        #Processes the e4 timestamps and sample rates. Together with the timings from the json it calculates the start and end indexes, to each signal_type (act, bvp, eda, ..) within each activity
        self.add_activity_indexes()

        #verify if error on input json
        self.number_of_timings = len(self.time_measures.keys())
        if(self.number_of_timings) < min_number_of_timings:
            #37 because epoch was added
            print("ERROR INPUT FILE: There is something wrong with the json: ",self.json_filename)
            print("The input json has ", self.number_of_timings, " entries")

        if len(self.e4_events.keys()) != 1:
            print("ERROR ON E4 EVENTS DICTIONARY: More than 1 event")

    def add_time_interval(self, exercise_name, begin_key, end_key):
        print(exercise_name, begin_key, end_key)
        self.experiments_timings[exercise_name] = {'begin_time': self.time_measures[begin_key] - self.computer_reference, 'end_time': self.time_measures[end_key] - self.computer_reference}
    
    def insert_relative_timings(self):
        #BREATHING TEST part is always between t2 and t3
        self.add_time_interval('breathing_test', 't2', 't3')

        #REACTION TEST is always between t4 and t5. The reaction_times are already computed and in variables called reaction_0 ... reaction_4
        self.add_time_interval('complete_reaction', 't4', 't5')
        #note: reaction times in the file are from range: t40...t49 -> 9 times. E.g: The reaction time for second test is t43-t42. However, before the reaction there is 
        #waiting period for the patient. Therefore, the total data for test 1 has to include this timings. Hence:
        self.add_time_interval('reaction_0', 't4', 't41')
        self.add_time_interval('reaction_1', 't41', 't43')
        self.add_time_interval('reaction_2', 't43', 't45')
        self.add_time_interval('reaction_3', 't45', 't47')
        self.add_time_interval('reaction_4', 't47', 't5')
        #note: time t5 and t49 measure the samething. It would also be "correct" to ignore t5 and only consider t49. But it would be less correct, as we might loose data points.
       
        #SIGNATURE is between t6 and t7. We have 5 different signatures: the timings are stored in variables t60,...,t64
        self.add_time_interval('complete_signature', 't6', 't7')
        self.add_time_interval('signature_0', 't6', 't60')
        self.add_time_interval('signature_1', 't60', 't61')
        self.add_time_interval('signature_2', 't61', 't62')
        self.add_time_interval('signature_3', 't62', 't63')
        self.add_time_interval('signature_4', 't63', 't7')
        #note: time t64 and t7 measure the samething. It would also be "correct" to ignore t7 and only consider t64.But it would be less correct, as we might loose data points.

        #TMA is between t8 and t9
        self.add_time_interval('tma_test', 't8', 't9')

        #TMB is between t10 and 11
        self.add_time_interval('tmb_test', 't10', 't11')

        #PHYSICAL TEST between t12 and t13
        self.add_time_interval('physical_test', 't12', 't13')
        
        self.add_time_interval('physical_0', 't12', 't120')
        self.add_time_interval('physical_1', 't120', 't121')
        self.add_time_interval('physical_2', 't121', 't122')
        self.add_time_interval('physical_3', 't122', 't123')
        self.add_time_interval('physical_4', 't123', 't13')
         
    def insert_reaction_times(self):
        #store the reaction times that were measured by the computer
        self.experiments_timings['reaction_0']['measure'] = self.time_measures['reaction_0']
        self.experiments_timings['reaction_1']['measure'] = self.time_measures['reaction_1']
        self.experiments_timings['reaction_2']['measure'] = self.time_measures['reaction_2']
        self.experiments_timings['reaction_3']['measure'] = self.time_measures['reaction_3']
        self.experiments_timings['reaction_4']['measure'] = self.time_measures['reaction_4']
    
    def add_activity_indexes(self):
        
        #create dictionary for each experiments part: breathing, signature, ...
        for key in self.experiments_timings.keys():
            self.experiments_indexes[key] = {}

        #inside each experiment part create dictionary to add the different signals: act, bvp, eda,...
        for key in self.experiments_indexes.keys():
            self.experiments_indexes[key]['ACT'] = {}
            self.experiments_indexes[key]['BVP'] = {}
            self.experiments_indexes[key]['EDA'] = {}
            self.experiments_indexes[key]['TEMP'] = {}
            #self.experiments_indexes[key]['IBI'] = {} WARNING: INTERBEATS INTERVALS ARE DIFFERENT
            self.experiments_indexes[key]['HR'] = {}

        #calculate begin and end index for each signal type within each exercise part
        for exercise in self.experiments_timings.keys():
            for signal_type in self.experiments_indexes[exercise].keys():
                print(exercise, signal_type)
                (start_ind, end_ind) = self.calculate_index(exercise, signal_type)
                self.experiments_indexes[exercise][signal_type]['start_index'] = ceil(start_ind)
                self.experiments_indexes[exercise][signal_type]['end_index'] = ceil(end_ind)
    
    def process_ACT_timestamp_sample_rate(self):
        #this method is more or less useless: the only goal if timestamps and sample rates for each actigraphy axis are equal. 99.9% they will, but just to be sure
        #if they aren't equal an exception is raised. otherwise it deletes the info for each axis and creates a unique one for all the axis indexes by 'ACT'
        try:
            if self.e4_timestamps['ACT_X'] != self.e4_timestamps['ACT_Y'] or self.e4_timestamps['ACT_X'] != self.e4_timestamps['ACT_Z'] or self.e4_timestamps['ACT_Y'] != self.e4_timestamps['ACT_Z']:
                raise Exception('DIFFERENT TIMESTAMPS on ACTIGRAPHY AXIS')
            
            if self.e4_sample_rates['ACT_X'] != self.e4_sample_rates['ACT_Y'] or self.e4_sample_rates['ACT_X'] != self.e4_sample_rates['ACT_Z'] or self.e4_sample_rates['ACT_Y'] != self.e4_sample_rates['ACT_Z']:
                raise Exception('DIFFERENT SAMPLE RATES on ACTIGRAPHY AXIS')

        except Exception as omg:
            print(type(omg))     # the exception omg
            print(omg.args)    # arguments stored in .args
            print(omg)
            return  #does this really stop it from executing the next code?
        
        #if sample rates and timestamps and equal, then:
        self.e4_timestamps['ACT'] = self.e4_timestamps['ACT_X']
        self.e4_sample_rates['ACT'] = self.e4_sample_rates['ACT_X']

        #delete entries for X Y and Z as they are redundant
        del self.e4_timestamps['ACT_X']
        del self.e4_timestamps['ACT_Y']
        del self.e4_timestamps['ACT_Z']
        
        del self.e4_sample_rates['ACT_X']
        del self.e4_sample_rates['ACT_Y']
        del self.e4_sample_rates['ACT_Z']
        
    def calculate_index(self, exercise_name, signal_type):
        #exercise name is either: breathing, signature, etc
        #signal type is: 'ACT', 'BVP', etc
        #output: start and end index for the specific signal type within an exercise (since the signals have different sample rates).
        e4_offset = self.e4_events[0] - self.e4_timestamps[signal_type]

        #start is the number of acquired samples between the e4 initial timestamp and the beggining of this activity
        start = self.e4_sample_rates[signal_type] * ( e4_offset + self.experiments_timings[exercise_name]['begin_time'] )
        end = self.e4_sample_rates[signal_type] * (e4_offset + self.experiments_timings[exercise_name]['end_time'] )

        return (start, end)

    def print_indexes(self):
        for signal_type in self.experiments_indexes['breathing_test'].keys():
            for exercise in self.experiments_indexes.keys():
                print("(", exercise, ",", signal_type, "):[", self.experiments_indexes[exercise][signal_type]['start_index'], ",", self.experiments_indexes[exercise][signal_type]['end_index'], "]")

class sessionObject:
    #class variables
    ACT = "/ACC.csv"
    BVP = "/BVP.csv"
    EDA = "/EDA.csv"
    HR = "/HR.csv"
    IBI = "/IBI.csv"
    TAGS = "/tags.csv"
    TEMP = "/TEMP.csv"

    def __init__(self, session_folder, input_json):
        #stores timestamp and samplerates of each csv file
        self.e4_timestamps = {}
        self.e4_sample_rates = {}
        self.e4_events = {}

        self.act = self.input_parser("ACT", session_folder + sessionObject.ACT, 3, ['X', 'Y', 'Z'])
        self.bvp = self.input_parser("BVP", session_folder + sessionObject.BVP, 1)
        self.eda = self.input_parser("EDA", session_folder + sessionObject.EDA, 1)
        self.hr = self.input_parser("HR", session_folder + sessionObject.HR, 1)
        self.ibi = self.input_parser("IBI", session_folder + sessionObject.IBI, 2)
        self.temp = self.input_parser("TEMP", session_folder + sessionObject.TEMP, 1)
        
        self.data = {'ACT': self.act, 'BVP': self.bvp, 'EDA': self.eda, 'HR': self.hr, 'IBI': self.ibi[1], 'TEMP': self.temp}

        self.insert_events(session_folder + sessionObject.TAGS)

        self.sync =  syncObject(input_json, self.e4_timestamps, self.e4_sample_rates, self.e4_events)

    def input_parser(self, exercise, filename, number_columns, cols = None):
        #input: E4's csv files
        #output: pandas series structure with input as floats
        with open(filename, 'r') as raw:
            lines = raw.readlines()
        
        #remove first line to get timestamp
        first_line = lines.pop(0)
        first_line = first_line.replace('IBI', '69696969') #this is just because there should be no strings on the csv files. But the IBI file doesn't make sense...
        first_line = first_line.replace('\n','')
        first_line = first_line.split(',')
        stamps = np.asarray(first_line, dtype = float)

        if exercise == "IBI":
            #IBI file has no timestamp, so only remove first line
            self.e4_timestamps[exercise] = stamps[0]
        else:
            #on the other files, the first two rows should be removed
            second_line = lines.pop(0)
            second_line = second_line.replace('\n','')
            second_line = second_line.split(',')
            rates = np.asarray(second_line, dtype = float)

            if exercise == "ACT":
                self.e4_timestamps[exercise + "_X"] = stamps[0]
                self.e4_sample_rates[exercise + "_X"] = rates[0]

                self.e4_timestamps[exercise + "_Y"] = stamps[1]
                self.e4_sample_rates[exercise + "_Y"] = rates[1]

                self.e4_timestamps[exercise + "_Z"] = stamps[2]
                self.e4_sample_rates[exercise + "_Z"] = rates[2]

            else:
                self.e4_timestamps[exercise] = stamps[0]
                self.e4_sample_rates[exercise] = rates[0]

        input_as_float = np.zeros((len(lines),number_columns), dtype = float)

        for i in range(len(lines)):
            lines[i] = lines[i].replace('\n', '')
            lines[i] = lines[i].split(',')
            input_as_float[i] = np.asarray(lines[i], dtype = float)

        return pd.DataFrame(input_as_float, columns = cols)
    
    def insert_events(self, filename):
        with open(filename, 'r') as raw:
            lines = raw.readlines()

        for i in range(len(lines)):
            actual_line = lines.pop(i)
            actual_line = actual_line.replace('\n','')

            stamp = np.asarray(actual_line, dtype = float)
            self.e4_events[i] = stamp
        
        if len(self.e4_events.keys()) != 1:
            print("WARNING THE WRISTBAND HAS MORE THAN ONE EVENT!!!!!!!")

#PLOTTING FUNCTIONS
    
def plot_ibi(ibi_data, start, end):
    ibi_data[1][start:end].plot()

def plot_data(data_dic, signal_type, start, end):
    plt.plot(data_dic[signal_type][start:end])


def plot_exercise(sessionObj, exercise_name):
    exercise_indexes = sessionObj.sync.experiments_indexes[exercise_name]
    
    plt.figure()
    counter = 1

    for signal_type in exercise_indexes.keys():
        if signal_type == 'IBI':
            #find out how to do this
            continue
        
        plt.subplot(int("23" + str(counter)))
        plt.title(signal_type + " - " + exercise_name)
        plot_data(sessionObj.data, signal_type, exercise_indexes[signal_type]['start_index'], exercise_indexes[signal_type]['end_index'])
        
        counter += 1

    plt.show()

    return counter
def plot_all_exercises(sessionObj):
    all_exercises = sessionObj.sync.experiments_indexes.keys()

    for exercise in all_exercises:
        counter = plot_exercise(sessionObj, exercise)
        print(counter)
    
    print("ended")
    #plt.show()

def plot_complete_data(sessionObj):   
    plt.figure()
    counter = 1
    
    for signal_type in sessionObj.data.keys():
        plt.subplot(int("23" + str(counter)))
        plt.title(signal_type + " - " + "COMPLETE SESSION DATA")
        plt.plot(sessionObj.data[signal_type])
        counter += 1

    plt.show()

def show():
    plt.show()


#CONTROL VARIABLE: The input json should have size 35, at least. If the patient made an error on PVT, then there should be more.
min_number_of_timings = 35

data_folder = "E4 Data"
json_input_file = data_folder + "/joana_moreira_1521822801-4188626.json"
#open accelerometer file
session_folder = data_folder + "/1521822749_A01251"

completeData = sessionObject(session_folder, json_input_file)

print("%%%%%%%%%%%% - INPUT DISPLAY - %%%%%%%%%%%%%%%")
pprint(completeData.sync.time_measures)

print("\n\n")

print("%%%%%%%%%%%% - EXPERIMENT TIMINGS DISPLAY - %%%%%%%%%%%%%%%")
pprint(completeData.sync.experiments_timings)

#try to plot something ?? not working
print("%%%%%%%%%%%% - ACTIGRAPHY DISPLAY - %%%%%%%%%%%%%%%")
pprint(completeData.act)

print("%%%%%%%%%%%% - TRY TO PRINT ACTIGRAPHY - %%%%%%%%%%%%%%%")
#plt.figure()
#completeData.act[:][2:len(completeData.act)].plot()
#plt.show()

#to debug something:
# with open(session_folder + "/ACC.csv", 'r') as raw:
#     lines = raw.readlines()

