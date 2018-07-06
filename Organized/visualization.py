import matplotlib.pyplot as plt
from math import ceil
import numpy as np

class DataVisualization:
    def __init__(self, sessionObject):
        self.sessionObject = sessionObject

    def task_actigraphy(self, option):
        title = "Visualization of Actigraphy Magnitude - Tasks"

        data_list = []

        for taskObject in self.sessionObject.taskObjectsList:
            data_list.append({'label': taskObject.name, 'values': taskObject.task_data["ACC_MAG"], 'indexes': taskObject.task_indexes, 'type': "ACC"})

        if option == "single":
            self.single_plot(title, "Magnitude", "Samples", data_list, "normal")
        elif option == "multiple":
            nr = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
            nc = 2

            self.multiple_plot(title, nr, nc, "Magnitude", "Time", data_list, "normal")
        else:
            print("Data Visualization: task_actigraphy(option) - Unknown option")

    def actigraphy_magnitude_alternatives(self):
        title = "Visualization of Actigraphy Magnitude - Alternatives"

        data_list = []
        data_list.append({'label': "Original", 'values': self.sessionObject.empaticaObject.data_final["ACC_MAG"]})
        data_list.append({'label': "Alternative", 'values': self.sessionObject.empaticaObject.data_final["ACC_MAG_ALT"]})

        fig, ax = plt.subplots()

        for item in data_list:
            ax.plot(item['values'], label = item['label'])

        ax.legend()
        ax.set_title(title)
        fig.canvas.set_window_title("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id, self.sessionObject.experiment_number))
        plt.ylabel("Magnitude")
        plt.xlabel("Samples")

    def autocorrelation_visualization(self, option):
        data_list = []

        for taskObject in self.sessionObject.taskObjectsList:
            data_list.append({'label': taskObject.name, 'values': taskObject.actigraphy_features.autocorrelation})

        if option == "multiple":
            nr = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
            nc = 2
            self.multiple_plot("Autocorrelation Visualization", nr, nc, "AutoCorr", "Lag", data_list, "normal")

        if option == "single":
            self.single_plot("Autocorrelation Visualization", "AutoCorr", "Lag", data_list, "normal")

    def psd_visualization(self, option):
        data_list = []

        for taskObject in self.sessionObject.taskObjectsList:
            data_list.append({'label': taskObject.name, 'values': taskObject.actigraphy_features.P_dens, 'freq': taskObject.actigraphy_features.freq})

        if option == "multiple":
            nr = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
            nc = 2
            self.multiple_plot("PSD Visualization", nr, nc, "PSD", "Freq", data_list, "semilogy")

        elif option == "single":
            self.single_plot("PSD Visualization", "PSD", "Freq", data_list, "semilogy")

    def ar_coefficients_visualization(self, option):
        data_list = []

        for taskObject in self.sessionObject.taskObjectsList:
            # Insert value 0 at the beginning of ar_coefficients array to simulate a constant term
            data_list.append({'label': taskObject.name + "_mine", 'values': np.insert(taskObject.actigraphy_features.yule_walker.ar_coefficients, 0, 0)})
            data_list.append({'label': taskObject.name + "_statsmodel", 'values': taskObject.actigraphy_features.yule_walker.AR_model_fit.params})

        if option == "multiple":
            nr = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
            nc = 2
            self.multiple_plot("AR Coefficients Visualization", nr, nc, "AR", "Index", data_list, "normal")

        elif option == "single":
            self.single_plot("AR Coefficients Visualization", "AR", "Index", data_list, "normal")

    def ar_model_predictions(self, option):
        data_list = []

        for taskObject in self.sessionObject.taskObjectsList:
            yule_walker = taskObject.actigraphy_features.yule_walker
            n_points = len(taskObject.actigraphy_features.magnitude_detrended)
            data_list.append({'label': taskObject.name, 'prediction' : yule_walker.prediction_v,
                              'prediction_statsmodel': yule_walker.prediction_v_statsmodel, 'original': taskObject.actigraphy_features.magnitude_detrended,
                              'horizontal_scale': np.linspace(0, n_points, num = n_points, endpoint = False) })

        if option == "multiple":
            nr = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
            nc = 2

            plt.figure("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id,
                                                                   self.sessionObject.experiment_number))
            plt.suptitle("AR Model Predictions")
            counter = 0

            for item in data_list:
                counter += 1
                plt.subplot(nr, nc, counter)
                plt.plot(item['horizontal_scale'], item['original'], label = "original")
                plt.plot(item['horizontal_scale'], item['prediction'], label = "prediction_mine")
                plt.plot(item['horizontal_scale'], item['prediction_statsmodel'], label = "prediction_statsmodel")
                plt.legend()
                plt.ylabel("ACC")
                plt.xlabel("Samples")
                plt.title(item['label'])

        elif option == "single":
            fig, ax = plt.subplots()

            for item in data_list:
                ax.plot(item['horizontal_scale'], item['original'], color = "yellow", label=item['label'] + "_original")
                ax.plot(item['horizontal_scale'], item['prediction'], color = "blue", label = item['label'] + "_prediction")
                ax.plot(item['horizontal_scale'], item['prediction_statsmodel'], color = "red", label = item['label'] + "_prediction_statsmodel")

            ax.legend()
            ax.set_title("AR Model Predictions")
            fig.canvas.set_window_title("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id,
                                                                              self.sessionObject.experiment_number))
            plt.ylabel("Value")
            plt.xlabel("Samples")


    def single_plot(self, title, y_label, x_label, data_list, mode):
        fig, ax = plt.subplots()
        if mode == "normal":
            for item in data_list:
                ax.plot(item['values'], label = item['label'])

            ax.legend()
            ax.set_title(title)
            fig.canvas.set_window_title("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id, self.sessionObject.experiment_number))
            plt.ylabel(y_label)
            plt.xlabel(x_label)

        elif mode == "semilogy":
            for item in data_list:
                ax.semilogy(item['freq'], item['values'], label = item['label'])

            ax.legend()
            ax.set_title(title)
            fig.canvas.set_window_title("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id, self.sessionObject.experiment_number))
            plt.ylabel(y_label)
            plt.xlabel(x_label)

        elif mode == "stem":
            for item in data_list:
                ax.plot(item['values'],  label = item['label'])

            ax.legend()
            ax.set_title(title)
            fig.canvas.set_window_title("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id, self.sessionObject.experiment_number))
            plt.ylabel(y_label)
            plt.xlabel(x_label)


    def multiple_plot(self, title, nr, nc, y_label, x_label, data_list, mode):
        plt.figure("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id, self.sessionObject.experiment_number))
        plt.suptitle(title)
        counter = 0

        if mode == "normal":
            for item in data_list:
                counter += 1
                plt.subplot(nr, nc, counter)

                # Building time scale
                #start_index = item['indexes'][item['type']]["start_index"]
                #end_index = item['indexes'][item['type']]["end_index"]
                #time_scale = self.sessionObject.time_scale[item["type"]][start_index:end_index]
                plt.plot(item['values'])
                #plt.plot(time_scale, item['values'])
                plt.ylabel(y_label)
                plt.xlabel(x_label)
                plt.title(item['label'])

        elif mode == "semilogy":
            for item in data_list:
                counter += 1
                plt.subplot(nr, nc, counter)
                plt.semilogy(item['freq'], item['values'])
                plt.ylabel(y_label)
                plt.xlabel(x_label)
                plt.title(item['label'])

        elif mode == "stem":
            for item in data_list:
                counter += 1
                plt.subplot(nr, nc, counter)
                plt.plot(item['values'], '.')
                plt.ylabel(y_label)
                plt.xlabel(x_label)
                plt.title(item['label'])

# class DataVisualization:
#     def compare_actigraphy_magnitude_alternatives(self):
#         data_list = []
#         data_list.append({'label': "Actigraphy Magnitude", 'values': self.sessionObject.empaticaObject.data_final["ACC_MAG"]})
#         data_list.append({'label': "Actigraphy Magnitude Alternative (Gravity)", 'values': self.sessionObject.empaticaObject.data_final["ACC_MAG_ALT"]})
#
#         fig, ax = plt.subplots()
#         for item in data_list:
#             ax.plot(item['values'], label = item['name'])
#
#         ax.legend()
#         ax.set_title("Actigraphy Magnitude Comparison")
#         plt.show()
#
#     def view_actigraphy_tasks_fft(self):
#         number_rows = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
#         number_columns = 2
#         counter = 0
#
#         plt.figure("Patiend: {} | Experiment: {} -- Actigraphy Spectral Magnitude Display".format(self.sessionObject.patient_id, self.sessionObject.experiment_number))
#         for taskObject in self.sessionObject.taskObjectsList:
#             counter += 1
#             plt.subplot(number_rows, number_columns, counter)
#             fft = taskObject.actigraphy_features.fft
#             for key in fft.keys():
#                 plt.loglog(fft[key]['freq_axis'], abs(fft[key]['values']), label = key)
#             #plt.loglog(fft["original"]['freq_axis'], fft["original"]['values'], label = "original")
#             plt.legend()
#             plt.title(taskObject.name)
#
#         plt.show()
#
#     def view_autocorrelation_tasks(self, title, ):
#         pass
#
#     def single_plot(self, title, data_list):
#         fig, ax = plt.subplots()
#
#         for item in data_list:
#             ax.plot(item('values'), label = item['label'])
#
#         ax.legend()
#         ax.set_title(title)
#         plt.show()
#
#     def multiple_plots(self, nr, nc, title, data_list):
#         counter = 0
#         plt.figure("Patient": {}


if __name__ == "__main__":
    patient = "D1"
    experiment = "1"
    experiment_number = int(experiment)
    base_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\"
    complete_folder = base_folder + patient + "\\" + experiment

    sessionObject = completeSession(patient, experiment_number, complete_folder)
    view = DataVisualization(sessionObject)