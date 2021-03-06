import os
import json
import copy
import numpy as np
from empatica import empaticaParser
from math import ceil       
import global_variables as gv

class timingsParser:
    def __init__(self, folder, first_event, stamps_dic, rates_dic, actigraphy_length):
        self.folder = folder
        self.json_filename = self.folder + "\\" + gv.get_json_filename(self.folder)
        self.timings = json.load(open(self.json_filename, 'r'))
        
        self.computer_epoch = self.timings['epoch_start']
        self.computer_reference = self.timings['experiment_start']
        self.experiment_timestamp = self.timings['timestamp_start']

        self.e4_event_epoch = first_event
        self.e4_signal_stamps = stamps_dic
        self.e4_signal_rates = rates_dic
        self.actigraphy_length = actigraphy_length
        
        #Contains start and end for each exercise. Measured relative to the variable self.computer_reference
        self.exercise_timings = self.build_exercise_timings()
        self.exercise_duration = self.build_exercises_duration()

        self.sub_exercise_timings = {}
        self.build_sub_exercise_timings()
        #self.sub_exercise_duration = self.build_sub_exercise_duration() DEVELOP THIS LATER

        #IMPORTANT: Develop code to tapping time series and reaction times to be returned to a feature object, instead of being stored here

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

        self.pause_indexes = self.build_pause_indexes()

        if self.check_if_wrong_task():
            # If there are any wrong tasks
            content = json.load(open(self.folder + "//wrong_task_correcao.json", 'r'))
            wrong_task = content["wrong_task"]

            print("DEBUG - Wrong Task: {}".format(wrong_task))
            self.pause_indexes = self.build_pause_indexes(wrong_task)
        else:
            self.pause_indexes = self.build_pause_indexes()

        self.experiment_label = self.build_experiment_label()

    def build_exercise_timings(self):
        timings_dictionary = {}
        for exercise in gv.EXERCISE_LIST:
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
        for exercise in gv.EXERCISE_LIST:
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
        for signal in gv.SIGNAL_LIST:
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
        
        start_index = self.e4_signal_rates[signal_type] * (e4_offset + begin_time)
        end_index = self.e4_signal_rates[signal_type] * (e4_offset + end_time)

        return (start_index, end_index)

    def build_pause_indexes(self, wrong_task = None):
        #generate dictionary between tasks
        new_dictionary = {}

        #deep copy of empatica's dictionary
        exercise_indexes = copy.deepcopy(self.exercise_indexes)

        #Setup in the beggining
        old_task = "beggining"
        exercise_indexes[old_task] = {}
        exercise_indexes[old_task]["ACC"] = {}
        exercise_indexes[old_task]["ACC"]["end_index"] = 0

        for task in self.exercise_indexes.keys():
            if task == wrong_task:
                continue
            else:
                key = old_task + "_" + task
                new_dictionary[key] = {}
                new_dictionary[key]["ACC"] = {'start_index': exercise_indexes[old_task]["ACC"]["end_index"], 'end_index': exercise_indexes[task]["ACC"]["start_index"]}
                old_task = task

        #Setup in the end
        if wrong_task == None:
            new_dictionary["physical_end"] = {}
            new_dictionary["physical_end"]["ACC"] = {"start_index": exercise_indexes["physical"]["ACC"]["end_index"], "end_index": self.actigraphy_length}
        else:
            # When a mistake was made and a task was repeated in the end, perform the following corrections:
            new_dictionary["physical_" + wrong_task] = {}
            new_dictionary["physical_" + wrong_task]["ACC"] = {"start_index": exercise_indexes["physical"]["ACC"]["end_index"], "end_index":exercise_indexes[wrong_task]["ACC"]["start_index"]}
            new_dictionary[wrong_task + "_end"] = {}
            new_dictionary[wrong_task + "_end"]["ACC"] = {"start_index": exercise_indexes[wrong_task]["ACC"]["end_index"], "end_index": self.actigraphy_length}

        return new_dictionary

    def build_experiment_label(self):
        stamp = self.experiment_timestamp.split(' ')
        aux = stamp[1].split(':')
        hours = int(aux[0])
        minutes = int(aux[1])

        if hours <= 12:
            return "morning"
        elif hours >= 14:
            return "afternoon"
        else:
            return "lunch"

    def check_if_wrong_task(self):
        for file in os.listdir(self.folder):
            if "wrong_task_correcao.json" in file:
                return True

        return False

if __name__ == "__main__":
    patient = "\\D3"
    experiment = "\\1"
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient + experiment

    empaticaObject = empaticaParser(complete_folder)
    timingsObject = timingsParser(complete_folder, empaticaObject.event_list[0], empaticaObject.stamps_dictionary, empaticaObject.rates_dictionary, len(empaticaObject.data_raw["ACC"]))

    exercise_indexes = timingsObject.exercise_indexes
    pause_indexes = timingsObject.pause_indexes
    empaticaObject.build_detrended_data(exercise_indexes, pause_indexes)
