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

        self.event_list = self.parse_events_file("/tags.csv")
        
        (self.stamps_dictionary, self.rates_dictionary) = self.parse_stamps_and_rate()

        self.data_raw = self.build_raw_data()

        self.actigraphy_length = len(self.data_raw["ACC"])

        # These structures will be filled uppon calling of method build_detrended_data()
        self.actigraphy_detrended = self.data_raw["ACC"].copy(deep = True)
        self.actigraphy_magnitude = None
        self.data_detrended = {}
        self.actigraphy_means_tasks = {}
        self.actigraphy_means_pauses = {}

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
                    print("Unexpected: Actigraphy axis with different sample timestamps")

                #verify is sample rate is equal for all axis
                if x_samplerate == y_samplerate == z_samplerate:
                    rates_dictionary[signal] = x_samplerate
                else:
                    print("WARNING: Actigraphy sample rate is different according to the axis!")
            
            else:
                #Store timestamp
                stamps_dictionary[signal] = float(first_line[0])
                
                #Store sample rate
                if(signal == "IBI"):
                    continue
                else:
                    rates_dictionary[signal] = float(second_line[0])

        return (stamps_dictionary, rates_dictionary)

    def parse_file(self, signal, number_columns, cols = None):
        with open(self.folder + "\\" + signal + ".csv", 'r') as raw:
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

        mean_vector = np.zeros(3)

        #Detrending by tasks
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
        
        for pause in existing_pauses_indexes.keys():
            task_indexes = existing_pauses_indexes[pause]

            start_index = task_indexes["ACC"]["start_index"]
            end_index = task_indexes["ACC"]["end_index"]

            data_slice = self.actigraphy_detrended[start_index:end_index]
            length = len(data_slice)

            for i, axis in enumerate(data_slice):
                mean_vector[i] = data_slice[axis].sum()/length
                self.actigraphy_means_pauses[task] = mean_vector
                self.actigraphy_detrended[axis][start_index:end_index] = self.actigraphy_detrended[axis][start_index:end_index] - mean_vector[i]

        self.actigraphy_magnitude = np.sqrt(self.actigraphy_detrended['X']**2 + self.actigraphy_detrended['Y']**2 + self.actigraphy_detrended['Z']**2)
        self.data_detrended = {'ACC': self.actigraphy_detrended, 'ACC_MAG': self.actigraphy_magnitude, 'BVP':  self.bvp_raw, 'EDA': self.eda_raw, 'HR': self.hr_raw, 'TEMP': self.temp_raw, 'IBI': self.ibi_raw}


if __name__ == "__main__":
    patient = "\\D1"
    experiment = "\\3"
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient + experiment

    empaticaObject = empatica(complete_folder)

    print(empaticaObject.event_list)

