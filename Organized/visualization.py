import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from session import CompleteSession
import global_variables as gv

class DataVisualization:
    def __init__(self, session_list):
        self.session_list = session_list
        self.patient_id = self.session_list[0].patient_id

        self.number_sessions = len(self.session_list)

        if self.number_sessions == 1:
            self.experiments = repr(self.session_list[0].experiment_number)
        else:
            self.experiments = repr(self.session_list[0].experiment_number) + "_" + repr(self.session_list[len(self.session_list) - 1].experiment_number)

    def raw_signals(self, analysis):
        data_structure = {}

        for signal in gv.SIGNAL_LIST:
            data_element = []
            for session in self.session_list:
                if signal == "ACC":
                    data_element.append({'value': session.empaticaObject.data_final["ACC_RAW"], 'experiment_number': session.experiment_number,
                                         'period': session.label, 'y_label': gv.UNITS["ACC"], 'x_label': "Samples"})
                else:
                    data_element.append({'value': session.empaticaObject.data_final[signal], 'experiment_number': session.experiment_number,
                                         'period': session.label, 'y_label': gv.UNITS[signal], 'x_label': "Samples"})

            if signal == "ACC":
                data_structure["ACC_RAW"] = data_element
            else:
                data_structure[signal] = data_element

        if analysis == "patient":
            self.plot(data_structure, "Raw Signals", "experiment_number", 3, 2)

        elif analysis == "group":
            self.plot_periods(data_structure, "Raw Signals", "period", 3, 2)

    def raw_detrended_signals(self, analysis):
        data_structure = {}

        for signal in gv.SIGNAL_LIST:
            data_element = []
            for session in self.session_list:
                if signal == "ACC":
                    data_element.append({'value': session.empaticaObject.data_final["ACC_DETRENDED"], 'experiment_number': session.experiment_number,
                                         'period': session.label, 'y_label': gv.UNITS["ACC"], 'x_label': "Samples"})
                else:
                    data_element.append({'value': session.empaticaObject.data_final[signal], 'experiment_number': session.experiment_number,
                                         'period': session.label, 'y_label': gv.UNITS[signal], 'x_label': "Samples"})
            if signal == "ACC":
                data_structure["ACC_DETRENDED"] = data_element
            else:
                data_structure[signal] = data_element

        if analysis == "patient":
            self.plot(data_structure, "Raw Detrended Signals", "experiment_number", 3, 2)

        elif analysis == "group":
            self.plot_periods(data_structure, "Raw Detrended Signals", "period", 3, 2)

    def raw_magnitude_signals(self, analysis):
        data_structure = {}

        for signal in gv.SIGNAL_LIST:
            data_element = []
            for session in self.session_list:
                if signal == "ACC":
                    data_element.append({'value': session.empaticaObject.data_final["ACC_MAG"],
                                         'experiment_number': session.experiment_number, 'period': session.label,
                                         'y_label': gv.UNITS["ACC"], 'x_label': "Samples"})
                else:
                    data_element.append({'value': session.empaticaObject.data_final[signal],
                                         'experiment_number': session.experiment_number, 'period': session.label,
                                         'y_label': gv.UNITS[signal], 'x_label': "Samples"})
            if signal == "ACC":
                data_structure["ACC_MAG"] = data_element
            else:
                data_structure[signal] = data_element

        if analysis == "patient":
            self.plot(data_structure, "Raw Magnitude Signals", "experiment_number", 3, 2)

        elif analysis == "group":
            self.plot_periods(data_structure, "Raw Magnitude Signals", "period", 3, 2)

    def task_actigraphy(self, analysis):
        data_structure = {}

        for task in gv.EXERCISE_LIST:
            data_element = []
            for session in self.session_list:
                if task in session.existing_tasks_indexes:
                    data_element.append({'value': session.taskObjectsDic[task].task_data["ACC_MAG"].values, 'experiment_number': session.experiment_number,
                                         'period': session.label, 'y_label': gv.UNITS["ACC"], 'x_label': "Samples"})
            data_structure[task] = data_element

        if analysis == "patient":
            self.plot(data_structure, "Task Actigraphy", "experiment_number", 5, 2)

        elif analysis == "group":
            self.plot_periods(data_structure, "Task Actigraphy", "period", 5, 2)

    def spectral_density(self, analysis):
        data_structure = {}
        for task in gv.EXERCISE_LIST:
            data_element = []
            for session in self.session_list:
                if task in session.existing_tasks_indexes:
                    data_element.append({'value': session.taskObjectsDic[task].actigraphy.yule_walker.dens_statsmodel,
                                        'freq_axis': session.taskObjectsDic[task].actigraphy.yule_walker.freq_statsmodel,
                                         'experiment_number': session.experiment_number, 'period': session.label, 'y_label': "dB/rad/Sample", "x_label": "Normalized Frequency"})
            data_structure[task] = data_element

        if analysis == "patient":
            self.plot(data_structure, "Spectral Density", "experiment_number", 5, 2)

        elif analysis == "group":
            self.plot_periods(data_structure, "Spectral Density", "period", 5, 2)

    def ar_coefficients(self, analysis):
        data_structure = {}

        for task in gv.EXERCISE_LIST:
            data_element = []
            for session in self.session_list:
                if task in session.existing_tasks_indexes:
                    data_element.append({'value': session.taskObjectsDic[task].actigraphy.yule_walker.ar_coefficients,
                                        'experiment_number': session.experiment_number, 'period': session.label,
                                         'y_label': 'Value', "x_label": "Coefficient"})
            data_structure[task] = data_element

        if analysis == "patient":
            self.plot(data_structure, "AR Coefficients", "experiment_number", 5, 2, "stem")

        elif analysis == "group":
            self.plot_periods(data_structure, "AR Coefficients", "period", 5, 2)

    def ar_fitting(self, analysis):
        data_structure = {}
        for task in gv.EXERCISE_LIST:
            data_element = []
            for session in self.session_list:
                if task in session.existing_tasks_indexes:
                    data_element.append({'predicted': session.taskObjectsDic[task].actigraphy.yule_walker.prediction_v_statsmodel,
                                        'data': session.taskObjectsDic[task].task_data["ACC_MAG"].values, 'experiment_number': session.experiment_number,
                                        'period': session.label, 'y_label': gv.UNITS["ACC"], 'x_label': "Samples"})
            data_structure[task] = data_element

        plt.figure()
        plt.suptitle("AR Fitting - " + "Patient:{} | Experiments: {}".format(self.patient_id, self.experiments))
        counter = 0

        for key in data_structure.keys():
            data_element = data_structure[key]
            counter += 1
            plt.subplot(5, 2, counter)

            for element in data_element:
                plt.plot(element['data'], label = "data")
                plt.plot(element['predicted'], label = "predicted")

            plt.legend(loc = "best")
            plt.ylabel(element["y_label"])
            plt.xlabel(element["x_label"])
            plt.title(key)

    def main(self, option, analysis):
        if option == "raw_signals":
            self.raw_signals(analysis)
        elif option == "raw_detrended_signals":
            self.raw_detrended_signals(analysis)
        elif option == "raw_magnitude_signals":
            self.raw_magnitude_signals(analysis)
        elif option == "task_actigraphy":
            self.task_actigraphy(analysis)
        elif option == "spectral_density":
            self.spectral_density(analysis)
        elif option == "ar_fitting":
            self.ar_fitting(analysis)
        elif option == "ar_coefficients":
            self.ar_coefficients(analysis)

    def plot(self, data_structure, title, label_key, nr, nc, display_mode = None):
        plt.figure()
        plt.suptitle(title + "Patient:{} | Experiments: {}".format(self.patient_id, self.experiments))
        counter = 0

        for key in data_structure.keys():
            data_element = data_structure[key]
            counter += 1
            plt.subplot(nr, nc, counter)

            for element in data_element:
                if key is "IBI":
                    plt.plot(element['value']['T'], element['value']['IBI'], label = element[label_key])
                elif key is "ACC_RAW" or key is "ACC_DETRENDED":
                    plt.plot(element['value']['X'], label = repr(element[label_key]) + "_X")
                    plt.plot(element['value']['Y'], label = repr(element[label_key]) + "_Y")
                    plt.plot(element['value']['Z'], label = repr(element[label_key]) + "_Z")
                else:
                    if display_mode == "stem":
                        plt.plot(element['value'], '.', label = element[label_key])
                    else:
                        plt.plot(element['value'], label = element[label_key])

            plt.legend(loc = "best")
            plt.ylabel(element["y_label"])
            plt.xlabel(element["x_label"])
            plt.title(key)

    def plot_periods(self, data_structure, title, label_key, nr, nc):
        plt.figure()
        plt.suptitle(title + "Patient:{} | Experiments: {}".format(self.patient_id, self.experiments))
        counter = 0

        for key in data_structure.keys():
            data_element = data_structure[key]
            counter += 1
            plt.subplot(nr, nc, counter)

            for element in data_element:
                if key is "IBI":
                    if element[label_key] == "morning":
                        plt.plot(element['value']['T'], element['value']['IBI'], color="red")
                    elif element[label_key] == "afternoon":
                        plt.plot(element['value']['T'], element['value']['IBI'], color="green")
                    elif element[label_key] == "lunch":
                        plt.plot(element['value']['T'], element['value']['IBI'], color="blue")

                elif key is "ACC_RAW" or key is "ACC_DETRENDED":
                    if element[label_key] == "morning":
                        plt.plot(element['value'], color="red")
                    elif element[label_key] == "afternoon":
                        plt.plot(element['value'], color="green")
                    elif element[label_key] == "lunch":
                        plt.plot(element['value'], color="blue")

                else:
                    if element[label_key] == "morning":
                        plt.plot(element['value'], color="red")
                    elif element[label_key] == "afternoon":
                        plt.plot(element['value'], color="green")
                    elif element[label_key] == "lunch":
                        plt.plot(element['value'],color="blue")

            red_patch = mpatches.Patch(color='red', label='Morning')
            green_patch = mpatches.Patch(color='green', label='Afternoon')
            blue_patch = mpatches.Patch(color='blue', label='Lunch')
            plt.legend(handles=[red_patch, green_patch, blue_patch])
            plt.ylabel(element["y_label"])
            plt.xlabel(element["x_label"])
            plt.title(key)

        #plt.legend(loc="best")

if __name__ == "__main__":
    patient = "D1"

    sessionList = []
    sessionList.append(CompleteSession(patient, 2, True))
    sessionList.append(CompleteSession(patient, 3, True))
    # sessionList.append(completeSession(patient, 3))

    visualization = DataVisualization(sessionList)
    visualization.main_method("raw_signals")