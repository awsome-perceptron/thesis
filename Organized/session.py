from empatica import empaticaParser
from timings import timingsParser
from panas import panasParser
from task import Task
from unit_testing import unitTesting

import matplotlib.pyplot as plt
import numpy as np

from math import ceil



class completeSession:
    #When creating this object search for exceptions for missing data
    def __init__(self, patient_id, experiment_number, folder):
        self.patient_id = patient_id
        self.experiment_number = experiment_number
        self.folder = folder
        self.experiment_number = experiment_number

        #Creation of  Empatica, Timings and Panas objects
        self.empaticaObject = empaticaParser(self.folder)
        self.timingsObject = timingsParser(self.folder, self.empaticaObject.event_list[0], self.empaticaObject.stamps_dictionary,
                                           self.empaticaObject.rates_dictionary, self.empaticaObject.actigraphy_length)
        self.panasObject = panasParser(self.folder)

        #Create list of existing tasks and pauses
        (self.existing_tasks_indexes, self.existing_pauses_indexes) = self.build_existing_lists(self.timingsObject.exercise_indexes, self.timingsObject.pause_indexes, self.empaticaObject.actigraphy_length)

        #Build pause indexes and detrend actigraphy data
        self.empaticaObject.build_detrended_data(self.existing_tasks_indexes, self.existing_pauses_indexes)

        #Creation of task objects list
        self.taskObjectsList = self.build_task_objects_list()

    def build_existing_lists(self, task_indexes, pause_indexes, actigraphy_length):
        #Calling: Try, Catch Exception dataSlicing and unexpected
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

    def fetch_task_data(self, task_indexes):
        task_data = {}

        for signal in self.empaticaObject.data_detrended.keys():
            if signal == "IBI":
                continue
            elif signal == "ACC_MAG":
                start_index = task_indexes["ACC"]["start_index"]
                end_index = task_indexes["ACC"]["end_index"]
            else:
                start_index = task_indexes[signal]["start_index"]
                end_index = task_indexes[signal]["end_index"]

            task_data[signal] = self.empaticaObject.data_detrended[signal][start_index:end_index]

        return task_data

    def build_task_objects_list(self):
        taskObjects_list = []
        for task_name in self.existing_tasks_indexes.keys():
            task_data = self.fetch_task_data(self.existing_tasks_indexes[task_name])
            task_indexes = self.existing_tasks_indexes[task_name]
            task_duration = self.timingsObject.exercise_duration[task_name]
            taskObjects_list.append(Task(task_name, task_duration, task_data, task_indexes, self.empaticaObject.actigraphy_means_tasks[task_name]))

        return taskObjects_list


if __name__ == "__main__":
    patient = "D1"
    experiment = "3"
    experiment_number = int(experiment)
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient + "\\" + experiment

    sessionObject = completeSession(patient, experiment_number, complete_folder)

    testing = unitTesting(sessionObject)

    #testing.print_head_of_tasks_data()

