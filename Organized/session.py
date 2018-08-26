from empatica import empaticaParser
from timings import timingsParser
from panas import panasParser
from task import Task
#from visualization import DataVisualization
import global_variables as gv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import pickle


class CompleteSession:
    #When creating this object search for exceptions for missing data
    def __init__(self, patient_id, experiment_number, fast_performance):
        self.patient_id = patient_id
        self.experiment_number = experiment_number
        self.folder = gv.BASE_FOLDER + patient_id + "\\" + repr(experiment_number)

        #Creation of  Empatica, Timings and Panas objects
        self.empaticaObject = empaticaParser(self.folder)
        self.timingsObject = timingsParser(self.folder, self.empaticaObject.event_list[0], self.empaticaObject.stamps_dictionary,
                                           self.empaticaObject.rates_dictionary, self.empaticaObject.actigraphy_length)
        self.panasObject = panasParser(self.folder)

        # Session attributes
        self.time_scale = self.empaticaObject.time_scale
        self.label = self.timingsObject.experiment_label
        self.fast_performance = fast_performance

        # Create list of existing tasks and pauses
        (self.existing_tasks_indexes, self.existing_pauses_indexes) = self.build_existing_lists(self.timingsObject.exercise_indexes, self.timingsObject.pause_indexes, self.empaticaObject.actigraphy_length)

        # Call method to detrend actigraphy data. Pass existing task and pause indexes, to detrend by blocks
        self.empaticaObject.build_detrended_data(self.existing_tasks_indexes, self.existing_pauses_indexes)

        # Creation of task objects list
        self.taskObjectsList, self.taskObjectsDic = self.build_task_objects_list()
        #self.taskObjectsList = self.testing_task_object()

        # Update or Load Yule Walker Objects
        self.update_or_load_yule_walker(fast_performance)

        # Set session features
        self.session_features = self.build_session_features()

    def build_existing_lists(self, task_indexes, pause_indexes, actigraphy_length):
        tasks_list = {}
        pauses_list = {}
        for task in task_indexes.keys():
            start_index = task_indexes[task]["ACC"]["start_index"]
            end_index = task_indexes[task]["ACC"]["end_index"]

            if end_index <= actigraphy_length and start_index <= actigraphy_length:
                tasks_list[task] = task_indexes[task]

        for pause in pause_indexes.keys():
            start_index = pause_indexes[pause]["ACC"]["start_index"]
            end_index = pause_indexes[pause]["ACC"]["end_index"]

            if end_index <= actigraphy_length and start_index <= actigraphy_length:
                pauses_list[pause] = pause_indexes[pause]

        return tasks_list, pauses_list

    def fetch_task_data(self, task_name, task_indexes):
        task_data = {}

        for signal in self.empaticaObject.data_final.keys():
            if signal == "ACC_MEANS":
                task_data[signal] = self.empaticaObject.data_final[signal][task_name]
                continue
            if signal == "IBI":
                continue
            elif signal == "ACC_MAG" or signal == "ACC_DETRENDED" or signal == "ACC_RAW":
                start_index = task_indexes["ACC"]["start_index"]
                end_index = task_indexes["ACC"]["end_index"]
            else:
                start_index = task_indexes[signal]["start_index"]
                end_index = task_indexes[signal]["end_index"]

            task_data[signal] = self.empaticaObject.data_final[signal][start_index:end_index]

        task_data["ACC_RAW_MEANS"] = self.empaticaObject.data_final["ACC_MEANS"][task_name]

        return task_data

    def build_task_objects_list(self):
        taskObjects_list = []
        taskObjects_dic = dict()

        for task_name in self.existing_tasks_indexes.keys():
            task_data = self.fetch_task_data(task_name, self.existing_tasks_indexes[task_name])
            task_indexes = self.existing_tasks_indexes[task_name]
            task_duration = self.timingsObject.exercise_duration[task_name]
            taskObject = Task(task_name, task_duration, task_data, task_indexes, self.fast_performance, self.folder)
            taskObjects_list.append(taskObject)
            taskObjects_dic[task_name] = taskObject

        return taskObjects_list, taskObjects_dic

    def testing_task_object(self):
        taskObjects_list = []

        task_name = "drawing"
        task_data = self.fetch_task_data(task_name, self.existing_tasks_indexes[task_name])
        task_indexes = self.existing_tasks_indexes[task_name]
        task_duration = self.timingsObject.exercise_duration[task_name]
        taskObjects_list.append(Task(task_name, task_duration, task_data, task_indexes, self.fast_performance, self.folder))

        return taskObjects_list

    def update_or_load_yule_walker(self, fast_performance):
        dictionary = dict()
        if fast_performance:
            # Load Yule Walker Objets
            with open(self.folder + "//" + "yule_walker.pkl", 'rb') as input:
                yule_walker = pickle.load(input)

                for task in self.existing_tasks_indexes.keys():
                    self.taskObjectsDic[task].actigraphy.yule_walker = yule_walker[task]
                    #print(self.taskObjectsDic[task].actigraphy_features.yule_walker.ar_coefficients)

        else:
            # Update Yule Walker Objects
            for task in self.existing_tasks_indexes.keys():
                dictionary[task] = self.taskObjectsDic[task].actigraphy.yule_walker

            with open(self.folder + "//" + "yule_walker.pkl", 'wb') as output:
                pickle.dump(dictionary, output, pickle.HIGHEST_PROTOCOL)

    def build_session_features(self):
        # Call method to set the features of each task (has to be done manually because yule walker class is empty on the begging, on fast performance)
        for task in self.taskObjectsList:
            task.build_task_features()

        # Store all session features on the following dictionary
        session_features = dict()
        session_features['patient_id'] = self.patient_id
        session_features['experiment_number'] = self.experiment_number
        session_features['label'] = self.label
        session_features['PA'] = self.panasObject.panas_series['PA']
        session_features['NA'] = self.panasObject.panas_series['NA']

        for task in self.existing_tasks_indexes.keys():
            session_features[task] = self.taskObjectsDic[task].task_features

        return session_features


if __name__ == "__main__":
    initial_time = time.perf_counter()
    patient = "H1"
    experiment = "3"
    experiment_number = int(experiment)
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    folder = base_folder + patient + "\\" + experiment

    ini_time = time.perf_counter()
    sessionObject = CompleteSession(patient, experiment_number, False)
    yule_walker = sessionObject.taskObjectsDic["drawing"].actigraphy.yule_walker
    teste = sessionObject.session_features

    end_time = time.perf_counter()
    print("Time to run: {}".format(end_time - ini_time))