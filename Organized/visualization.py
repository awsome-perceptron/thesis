import matplotlib.pyplot as plt
from math import ceil
import numpy as np
import global_variables as gv
from session import completeSession

class DataVisualization:
    def __init__(self, sessionObject):
        self.sessionObject = sessionObject

    def task_data(self, option):
        pass

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
            #data_list.append({'label': taskObject.name + "_mine", 'values': np.insert(taskObject.actigraphy_features.yule_walker.ar_coefficients, 0, 0)})
            data_list.append({'label': taskObject.name + "_statsmodel", 'values': taskObject.actigraphy_features.yule_walker.AR_model_fit.params})

        if option == "multiple":
            nr = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
            nc = 2
            self.multiple_plot("AR Coefficients Visualization", nr, nc, "AR", "Index", data_list, "stem")

        elif option == "single":
            self.single_plot("AR Coefficients Visualization", "AR", "Index", data_list, "stem")

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

            plt.figure()
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

    def power_spectral_density(self, option):
        data_list = []

        for taskObject in self.sessionObject.taskObjectsList:
            yule_walker = taskObject.actigraphy_features.yule_walker
            data_list.append({'label': taskObject.name, 'values': yule_walker.dens, 'values_statsmodel': yule_walker.dens_statsmodel,
                              'periodogram': taskObject.actigraphy_features.P_dens,'horizontal_scale': yule_walker.freq})

        if option == "single":
            fig, ax1 = plt.subplots()

            for item in data_list:
                #ax.plot(item['horizontal_scale'], item['periodogram'], label=item['label'] + "_periodogram")
                #ax1.plot(item['horizontal_scale'], item['values'], label = item['label'] + "_mine")
                ax1.plot(item['horizontal_scale'], item['values_statsmodel'], label = item['label'] + "_statsmodel")

            ax1.legend()
            ax1.set_title("PSD Estimation")
            fig.canvas.set_window_title("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id,
                                                                              self.sessionObject.experiment_number))

            plt.ylabel("PSD (dB/rad/sample)")
            plt.xlabel(r'Normalized Frequency ($\times \pi$rad/sample)')

        elif option == "multiple":
            nr = ceil(len(self.sessionObject.existing_tasks_indexes)/2)
            nc = 2

            plt.figure()
            #plt.figure("Patient: {} | Experiment: {}".format(self.sessionObject.patient_id,
            #                                                 self.sessionObject.experiment_number))
            plt.suptitle("AR Model Predictions")
            counter = 0

            for item in data_list:
                counter += 1
                plt.subplot(nr, nc, counter)
                #plt.plot(item['horizontal_scale'], item['periodogram'], label="periodogram")
                #plt.plot(item['horizontal_scale'], item['values'], label="psd_mine")
                plt.plot(item['horizontal_scale'], item['values_statsmodel'], label="psd_statsmodel")
                plt.legend()
                plt.ylabel("PSD (dB/rad/sample)")
                plt.xlabel(r'Normalized Frequency ($\times \pi$rad/sample)')
                plt.title(item['label'])

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
                ax.plot(item['values'], '.', label = item['label'])

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


class MultipleVisualization:
    def __init__(self, sessionList):
        self.sessionList = sessionList

        self.structured_data = self.structure_data()

    def structure_data(self):
        # Returns a dictionary indexed by task names. Each entry has an array of Task Objects corresponding to the different experiments
        all_sessions = dict()

        for task in gv.EXERCISE_LIST:
            data_list = []

            for i in range(len(self.sessionList)):
                if task in self.sessionList[i].taskObjectsDic.keys():
                    data_list.append({'task_object': self.sessionList[i].taskObjectsDic[task], 'patient_id': self.sessionList[i].patient_id,
                                      'experiment_number': self.sessionList[i].experiment_number, 'label': self.sessionList[i].label})
                else:
                    data_list.append({'task_object': None, 'experiment_number': self.sessionList[i].experiment_number})

            all_sessions[task] = data_list

        return all_sessions

    def power_spectral_density(self):
        data_object = dict()

        for task in self.structured_data:
            data_object[task] = []
            task_list = self.structured_data[task]

            for i in range(len(task_list)):
                if task_list[i]["task_object"] is None:
                    print("None detected")
                else:
                    task_obj = task_list[i]["task_object"]
                    experiment = task_list[i]["experiment_number"]

                    # Afterwards add label to data_list
                    data_object[task].append({'density': task_obj.actigraphy_features.yule_walker.dens_statsmodel, 'freq': task_obj.actigraphy_features.yule_walker.freq_statsmodel,
                                              'experiment_number': experiment, 'label': task_list[i]["label"]})

        self.multiple_plot(data_object, "PSD Estimation", 5, 2, "dB/rad/sample", r'Normalized Frequency ($\times \pi$rad/sample)', 'density', 'freq')

    def multiple_plot(self, data_object, title, nr, nc, y_label, x_label, y_tag, x_tag):
        plt.figure()
        plt.suptitle(title)
        counter = 0

        for task in data_object:
            counter += 1
            plt.subplot(nr, nc, counter)
            for item in data_object[task]:
                plt.plot(item[x_tag], item[y_tag], label = item["label"])

            plt.legend()
            plt.ylabel(y_label)
            plt.xlabel(x_label)
            plt.title(task)

if __name__ == "__main__":
    patient = "D1"

    sessionList = []
    sessionList.append(completeSession(patient, 1))
    print("First")
    sessionList.append(completeSession(patient, 2))
    print("Second")
    sessionList.append(completeSession(patient, 3))
    print("Third")

    multiple_view = MultipleVisualization(sessionList)
    structured_data = multiple_view.structured_data
    multiple_view.power_spectral_density()
    plt.show()