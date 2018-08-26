import os
import copy
import numpy as np
import global_variables as gv
import pandas as pd
#GLOBAL VARIABLES:

class empaticaParser:
    def __init__(self, folder):
        self.folder = folder

        self.zip_filename = gv.get_zip_filename(self.folder)
        if self.zip_filename is None:
            print("Zip file not found")
            return

        self.event_list = self.parse_events_file("/tags.csv")
        if self.event_list is None:
            print("ERROR: Events file is empty!")
            return
        
        (self.stamps_dictionary, self.rates_dictionary) = self.parse_stamps_and_rate()

        self.data_raw = self.build_raw_data()
        self.time_scale = self.build_time_scales()

        self.actigraphy_length = len(self.data_raw["ACC"])

        # These structures will be filled uppon calling of method build_detrended_data()
        self.actigraphy_detrended = None
        self.actigraphy_magnitude = None
        #self.alternative_actigraphy_magnitude = None
        self.data_detrended = {}
        self.actigraphy_means_tasks = {}
        self.actigraphy_means_pauses = {}
        self.data_final = {}

    def parse_events_file(self, tag_filename):
        with open(self.folder + tag_filename, 'r') as raw:
            lines = raw.readlines()

        number_lines = len(lines)

        if number_lines == 0:
            print("Unexpected: {} has zero lines!".format(tag_filename))
            return None
        
        #Pop first line
        first_line = lines.pop(0)
        first_line = first_line.replace('\n', '')
        
        if number_lines == 1:
            #Only one event
            return [float(first_line),]
        
        elif number_lines == 2:
            second_line = lines.pop(0)
            second_line = second_line.replace('\n', '')
            return [float(first_line), float(second_line)]

        else:
            print("Unexpected: Tags.csv with more than 2 events!")
            return [float(first_line),]

    def parse_stamps_and_rate(self):
        stamps_dictionary = {}
        rates_dictionary = {}

        for signal in gv.SIGNAL_LIST:
            with open(self.folder + "\\" + signal + ".csv", 'r') as f:
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
                    stamps_dictionary[signal] = x_timestamp
                else:
                    print("WARNING: Actigraphy timestamps of different axis don't match!")

                #verify is sample rate is equal for all axis
                if x_samplerate == y_samplerate == z_samplerate:
                    rates_dictionary[signal] = x_samplerate
                else:
                    print("WARNING: Actigraphy sample rate of different axis don't match!")
            
            else:
                #Store timestamp
                if first_line == ['']:
                    print("WARNING: File ", signal, ".csv is EMPTY in folder ", self.folder)
                else:
                    stamps_dictionary[signal] = float(first_line[0])

                #Store sample rate
                if(signal == "IBI"):
                    # IBI File has no sample rate. The structure of this file is different
                    continue
                else:
                    rates_dictionary[signal] = float(second_line[0])

        return (stamps_dictionary, rates_dictionary)

    def parse_file(self, signal, number_columns, cols = None):
        with open(self.folder + "\\" + signal + ".csv", 'r') as raw:
            lines = raw.readlines()

        if lines == []:
            print("WARNING: Ignoring file {}.csv".format(signal))
            return None
        else:
            discard = lines.pop(0) #discard first line

        if signal != "IBI":
            discard = lines.pop(0) #discard second line

        data_as_float = np.zeros((len(lines), number_columns), dtype = float)

        for i in range(len(lines)):
            lines[i] = lines[i].replace('\n', '')
            lines[i] = lines[i].split(',')
            data_as_float[i] = np.asarray(lines[i], dtype = float)

        return pd.DataFrame(data_as_float, columns = cols)
    
    def build_raw_data(self):
        self.actigraphy_raw = self.parse_file("ACC", 3, ['X', 'Y', 'Z'])
        self.bvp_raw = self.parse_file("BVP", 1)
        self.hr_raw = self.parse_file("HR", 1)
        self.eda_raw = self.parse_file("EDA", 1)
        self.temp_raw = self.parse_file("TEMP", 1)
        self.ibi_raw = self.parse_file("IBI", 2, ['T', 'IBI'])
        
        return {'ACC': self.actigraphy_raw, 'BVP':  self.bvp_raw, 'EDA': self.eda_raw, 'HR': self.hr_raw, 'TEMP': self.temp_raw, 'IBI': self.ibi_raw}

    def build_detrended_data(self, existing_tasks_indexes, existing_pauses_indexes):
        #This methods fills the attributes: actigraphy_means_tasks, actigraphy_means_pauses, data_detrended and actigraphy_magnitude

        self.actigraphy_detrended = self.data_raw["ACC"].copy(deep = True)
        mean_vector = np.zeros(3)

        #Detrending in tasks
        for task in existing_tasks_indexes.keys():
            task_indexes = existing_tasks_indexes[task]

            start_index = task_indexes["ACC"]["start_index"]
            end_index = task_indexes["ACC"]["end_index"]

            data_slice = self.actigraphy_detrended[start_index:end_index]
            length = len(data_slice)

            for i, axis in enumerate(data_slice):
                mean_vector[i] = data_slice[axis].sum()/length
                self.actigraphy_means_tasks[task] = mean_vector
                self.actigraphy_detrended[axis][start_index:end_index] = self.actigraphy_detrended[axis][start_index:end_index] - mean_vector[i]

        #Detrending by pauses
        for pause in existing_pauses_indexes.keys():
            task_indexes = existing_pauses_indexes[pause]

            start_index = task_indexes["ACC"]["start_index"]
            end_index = task_indexes["ACC"]["end_index"]

            # print(pause)
            # print("Start Index: {} | End Index: {}".format(start_index, end_index))
            # print(len(data_slice))

            data_slice = self.actigraphy_detrended[start_index:end_index]
            length = len(data_slice)

            for i, axis in enumerate(data_slice):
                mean_vector[i] = data_slice[axis].sum()/length
                self.actigraphy_means_pauses[task] = mean_vector
                self.actigraphy_detrended[axis][start_index:end_index] = self.actigraphy_detrended[axis][start_index:end_index] - mean_vector[i]

        self.actigraphy_magnitude = np.sqrt(self.actigraphy_detrended['X']**2 + self.actigraphy_detrended['Y']**2 + self.actigraphy_detrended['Z']**2)
        self.build_data_structure()

    # def alternative_actigraphy_detrending(self):
    #     # Method: Actigraphy data measures Earth's gravity. Calculate the magnitude of the vector and then subtract 1g
    #     # In the units of actigraphy, a value of 64 represents an acceleration of 1g
    #     # Problem: Using this method a lot of points are below zero, which shouldn't happen.
    #     # This is due to rotational movements.
    #
    #     # Calculation of the actigraphy magnitude
    #     self.alternative_actigraphy_magnitude = np.sqrt(self.actigraphy_raw['X']**2 + self.actigraphy_raw['Y']**2 + self.actigraphy_raw['Z']**2)
    #     # Subtraction of gravity
    #     self.alternative_actigraphy_magnitude = self.alternative_actigraphy_magnitude - 64

    def build_data_structure(self):
        #self.alternative_actigraphy_detrending() # Stores data in attribute self.alternative_actigraphy_magnitude
        # Removed entry with key: "ACC_MAG_ALT" with value: self.alternative_actigraphy_magnitude

        self.data_final = {'ACC_RAW': self.actigraphy_raw, 'ACC_DETRENDED': self.actigraphy_detrended,
                           'ACC_MEANS': self.actigraphy_means_tasks, 'ACC_MAG': self.actigraphy_magnitude,'BVP': self.bvp_raw, 'EDA': self.eda_raw,
                           'HR': self.hr_raw, 'TEMP': self.temp_raw, 'IBI': self.ibi_raw}

    def build_time_scales(self):
        time = {}
        for signal in self.rates_dictionary.keys():
            time[signal] = np.linspace(0, len(self.data_raw[signal])/self.rates_dictionary[signal], num = len(self.data_raw[signal]), endpoint = False)

        return time

if __name__ == "__main__":
    patient = "H7"
    experiment = "\\2"
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient + experiment

    empaticaObject = empaticaParser(complete_folder)


