import numpy as np
import time

class unitTesting:
    def __init__(self, sessionObject):
        self.sessionObject = sessionObject

    def subtract_gravity_count_below_threshold(self, threshold):
        print(" ----------------- Unit Testing: Actrigraphy Subtract Gravity Detrending - Number of Points Below Threshold ------------------")

        data = self.sessionObject.empaticaObject.data_final["ACC_MAG_ALT"]
        count = data[data < threshold].count()

        print("Total number of points: {} | Threshold: {} | Number of points below threshold: {} | Percentage: {}". format(len(data), threshold, count, round((count/len(data))*100,2)))

    def actigraphy_detrended_different_points(self):
        print("-------------------------  UNIT TESTING: Actigraphy Detrended Different Points  -----------------------")

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

    def print_actigraphy_means_dictionary(self):
        print("-------------------------  UNIT TESTING: Actigraphy Means Dictionary  -----------------------")

        dic = self.sessionObject.empaticaObject.actigraphy_means_tasks

        for task in dic.keys():
            print("Task name: ", task, " - (ux, uy, uz) = (", dic[task][0], ",", dic[task][1], ",", dic[task][2], ")")

    def print_timings_indexes_dictionarys(self):
        pauses_indexes = self.sessionObject.timingsObject.pause_indexes
        exercise_indexes = self.sessionObject.timingsObject.exercise_indexes

        print("\n Unit testing: Display of Pause and Exercise Indexes")

        print(" -------------------- Indexes of Tasks ---------------------- ")

        for task in exercise_indexes.keys():
            print("[ACC] - Task: {} - Start: {} - End: {}".format(task, exercise_indexes[task]["ACC"]["start_index"],
                                                                  exercise_indexes[task]["ACC"]["end_index"]))

        print(" ------------------- Indexes of Pauses ----------------------- ")
        for pause in pauses_indexes.keys():
            print("[ACC] - Pause: {} - Start: {} - End: {}".format(pause, pauses_indexes[pause]["ACC"]["start_index"],
                                                                 pauses_indexes[pause]["ACC"]["end_index"]))

        print("\n")

    def mean_of_detrended_actigraphy(self, existing_tasks_indexes, existing_pauses_indexes):
        mean_array = np.zeros(3)
        print(
            "\n Unit testing: Calculate mean of actigraphy signal")

        print(" ------------------- Mean inside Task segments ---------------------- ")

        for task in existing_tasks_indexes.keys():
            start = existing_tasks_indexes[task]["ACC"]["start_index"]
            end = existing_tasks_indexes[task]["ACC"]["end_index"]
            data = self.sessionObject.empaticaObject.data_detrended["ACC"][start:end]
            length = len(data)

            for i, axis in enumerate(data):
                mean_array[i] = data[axis].sum() / length

            print("Task: {} - Mean Array: ({},{},{})".format(task, mean_array[0], mean_array[1], mean_array[2]))

        print(" ----------------------- Mean inside Pause segments -------------------- ")

        for task in existing_pauses_indexes.keys():
            start = existing_pauses_indexes[task]["ACC"]["start_index"]
            end = existing_pauses_indexes[task]["ACC"]["end_index"]
            data = self.sessionObject.empaticaObject.actigraphy_detrended[start:end]
            length = len(data)

            for i, axis in enumerate(data):
                mean_array[i] = data[axis].sum() / length

            print("Task: {} - Mean Array: ({},{},{})".format(task, mean_array[0], mean_array[1], mean_array[2]))

    def print_head_of_tasks_data(self):

        print("\n Unit testing: Display Head of Tasks Data")

        for taskObject in self.taskObjectList:
            data = taskObject.task_data

            print("\n --------------------------------- TASK: {} ---------------------------------------".format(taskObject.name))

            for signal in data.keys():
                print("\n -------------- Signal: {} ----------------".format(signal))
                print(data[signal].head(3))

        print("\n")