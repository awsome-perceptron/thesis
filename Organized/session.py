from empatica import empaticaParser
from timings import timingsParser
from panas import panasParser
from task import Task
from unit_testing import unitTesting
#from visualization import DataVisualization
import global_variables as gv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time


class completeSession:
    #When creating this object search for exceptions for missing data
    def __init__(self, patient_id, experiment_number):
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

        self.label =self.timingsObject.experiment_label

        #Create list of existing tasks and pauses
        (self.existing_tasks_indexes, self.existing_pauses_indexes) = self.build_existing_lists(self.timingsObject.exercise_indexes, self.timingsObject.pause_indexes, self.empaticaObject.actigraphy_length)

        #Build pause indexes and detrend actigraphy data
        self.empaticaObject.build_detrended_data(self.existing_tasks_indexes, self.existing_pauses_indexes)

        #Creation of task objects list
        self.taskObjectsList, self.taskObjectsDic = self.build_task_objects_list()
        #self.taskObjectsList = self.testing_task_object()

    def build_existing_lists(self, task_indexes, pause_indexes, actigraphy_length):
        tasks_list = {}
        pauses_list = {}
        for task in task_indexes.keys():
            start_index = task_indexes[task]["ACC"]["start_index"]
            end_index = task_indexes[task]["ACC"]["end_index"]

            if end_index < actigraphy_length:
                tasks_list[task] = task_indexes[task]

        for pause in pause_indexes.keys():
            start_index = pause_indexes[pause]["ACC"]["start_index"]
            end_index = pause_indexes[pause]["ACC"]["end_index"]

            if end_index < actigraphy_length:
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
            elif signal == "ACC_MAG" or signal == "ACC_DETRENDED" or signal == "ACC_RAW" or signal == "ACC_MAG_ALT":
                start_index = task_indexes["ACC"]["start_index"]
                end_index = task_indexes["ACC"]["end_index"]
            else:
                start_index = task_indexes[signal]["start_index"]
                end_index = task_indexes[signal]["end_index"]

            task_data[signal] = self.empaticaObject.data_final[signal][start_index:end_index]

        return task_data

    def build_task_objects_list(self):
        taskObjects_list = []
        taskObjects_dic = dict()

        for task_name in self.existing_tasks_indexes.keys():
            task_data = self.fetch_task_data(task_name, self.existing_tasks_indexes[task_name])
            task_indexes = self.existing_tasks_indexes[task_name]
            task_duration = self.timingsObject.exercise_duration[task_name]
            taskObject = Task(task_name, task_duration, task_data, task_indexes, self.empaticaObject.actigraphy_means_tasks[task_name])
            taskObjects_list.append(taskObject)
            taskObjects_dic[task_name] = taskObject

        return taskObjects_list, taskObjects_dic

    def testing_task_object(self):
        taskObjects_list = []

        task_name = "drawing"
        task_data = self.fetch_task_data(task_name, self.existing_tasks_indexes[task_name])
        task_indexes = self.existing_tasks_indexes[task_name]
        task_duration = self.timingsObject.exercise_duration[task_name]
        taskObjects_list.append(Task(task_name, task_duration, task_data, task_indexes,
                                     self.empaticaObject.actigraphy_means_tasks[task_name]))

        return taskObjects_list

if __name__ == "__main__":
    initial_time = time.perf_counter()
    patient = "D1"
    experiment = "1"
    experiment_number = int(experiment)
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient + "\\" + experiment

    sessionObject = completeSession(patient, experiment_number)

    # testing = unitTesting(sessionObject)
    #
    # view = DataVisualization(sessionObject)
    # #view.task_actigraphy("multiple")
    # #view.actigraphy_magnitude_alternatives()
    # #view.autocorrelation_visualization("single")
    # #view.psd_visualization("multiple")
    # #view.ar_coefficients_visualization("multiple")
    # view.ar_model_predictions("multiple")
    # view.power_spectral_density("multiple")
    # view.power_spectral_density("single")


    end_time = time.perf_counter()
    print("Time to Run: {}".format(end_time - initial_time))
    plt.show()

    #Declaration of variables to be easier to work inside interpreter
    task = sessionObject.taskObjectsList[0]
    features = task.actigraphy_features
    yule_walker = task.actigraphy_features.yule_walker

    #testing.print_head_of_tasks_data()


