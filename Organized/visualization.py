from session import completeSession
import matplotlib.pyplot as plt
from math import ceil
import numpy as np

class DataVisualization:
    def __init__(self, sessionObject):
        self.sessionObject = sessionObject

    def actigraphy_magnitude_task_single_plot(self):
        #Building data list to plot multiple signals
        data_list = []

        for taskObject in self.sessionObject.taskObjectsList:
            data_list.append({'task': taskObject.name, 'ACC_MAG': taskObject.task_data["ACC_MAG"]})

        # plt.figure("Hello World")
        fig, ax = plt.subplots()
        for data in data_list:
            ax.plot(data['ACC_MAG'], label=data['task'])

        ax.legend()
        ax.set_title("Actigraphy Magnitude")
        fig.canvas.set_window_title("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id, self.sessionObject.experiment_number))
        plt.show()

    def actigraphy_magnitude_tasks_multiple_plot(self):
        sample_rate = self.sessionObject.empaticaObject.rates_dictionary["ACC"]

        number_rows = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
        number_columns = 2

        counter = 0

        plt.figure("Patient: {} | Experiment: {} -- Actigraphy Magnitude".format(self.sessionObject.patient_id, self.sessionObject.experiment_number))
        for taskObject in self.sessionObject.taskObjectsList:
            counter += 1

            plt.subplot(number_rows, number_columns, counter)
            data = taskObject.task_data["ACC_MAG"]
            time, step = np.linspace(0, len(data)/sample_rate, num = len(data), endpoint = False, retstep = True)
            if step != sample_rate:
                print("Step different than sample rate")
            plt.plot(time, data)
            plt.legend(taskObject.name)
            plt.ylabel("Mag")
            plt.xlabel("Time in seconds")
            plt.title(taskObject.name)

        plt.show()


if __name__ == "__main__":
    patient = "D1"
    experiment = "1"
    experiment_number = int(experiment)
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient + "\\" + experiment

    sessionObject = completeSession(patient, experiment_number, complete_folder)
    view = DataVisualization(sessionObject)