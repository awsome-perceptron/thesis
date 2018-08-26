import global_variables as gv
import os
from session import CompleteSession
import pandas as pd


class Patient:
    def __init__(self, patient_id, fast_performance):
        self.patient_id = patient_id
        self.folder = gv.BASE_FOLDER + patient_id

        # Creation of lists to store the session objects
        self.session_list = list()
        self.morning_list = list()
        self.afternoon_list = list()
        self.lunch_list = list()

        # Build experiments
        for experiment in os.listdir(self.folder):
            session = CompleteSession(self.patient_id, int(experiment), fast_performance)
            self.session_list.append(session)
            if session.label == "morning":
                self.morning_list.append(session)
            elif session.label == "afternoon":
                self.afternoon_list.append(session)
            elif session.label == "lunch":
                self.lunch_list.append(session)

        drawing_dataframe = self.build_task_dataframes("signature")
        print(drawing_dataframe)

    def build_task_dataframes(self, task_name):
        experiment_number_list = list()
        label_list = list()
        duration_list = list()
        mean_list = list()
        total_variation_list = list()

        for session in self.session_list:
            experiment_number_list.append(session.experiment_number)
            label_list.append(session.label)
            if task_name in session.existing_tasks_indexes.keys():
                task = session.taskObjectsDic[task_name]

                duration_list.append(task.duration)
                mean_list.append(task.task_features["acc"]["mean"])
                total_variation_list.append(task.task_features["acc"]["tv"])
            else:
                duration_list.append(float('nan'))
                mean_list.append(float('nan'))
                total_variation_list.append(float('nan'))

        # Build dictionary to convert to dataframe
        d = {'exp_number': experiment_number_list, 'label': label_list, 'duration': duration_list, 'mean': mean_list, 'tv': total_variation_list}

        return pd.DataFrame(data=d)

    def feature_average_by_periods(self, task, type, feature):
        average_morning = 0
        average_afternoon = 0

        for session in self.morning_list:
            if task in session.existing_tasks_indexes.keys():
                average_morning += session.session_features[task][type][feature]
        average_morning = average_morning/len(self.morning_list)

        for session in self.afternoon_list:
            if task in session.existing_tasks_indexes.keys():
                average_afternoon += session.session_features[task][type][feature]
        average_afternoon = average_afternoon/len(self.afternoon_list)

        return average_morning, average_afternoon

    def print_average_by_periods(self):
        for type in gv.FEATURE_TYPES:
            for feature in gv.FEATURES[type]:
                for task in gv.EXERCISE_LIST:
                    morning, afternoon = self.feature_average_by_periods(task, type, feature)
                    print("Task: {} | Feature: {} | Morning: {} | Afternoon: {}".format(task, feature, morning, afternoon))

    def print_feature_by_periods(self, type, feature):
        print(" ---------- {} ------------".format(feature))
        for task in gv.EXERCISE_LIST:
            print("--------- {} | {} --------------".format(task,feature))
            print("Morning")
            for session in self.morning_list:
                if task in session.existing_tasks_indexes.keys():
                    print(session.session_features[task][type][feature], end="|")
            print("")

            print("Afternoon")
            for session in self.afternoon_list:
                if task in session.existing_tasks_indexes.keys():
                    print(session.session_features[task][type][feature], end="|")
            print("")

    def print_all_features_by_periods(self):
        for type in gv.FEATURE_TYPES:
            for feature in gv.FEATURES[type]:
                self.print_feature_by_periods(type, feature)



if __name__ == "__main__":
    patient_id = "D1"
    patient = Patient(patient_id, True)

