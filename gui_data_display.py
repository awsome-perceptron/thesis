from separation_indexes_calculation import empaticaParser, timingsParser, SAMPLE_RATES
from patient_gui_interface import DatabaseObject
import sqlite3
from tkinter import *
import tkinter as tk
from tkinter.font import Font
import os
import zipfile
from math import ceil
import numpy as np
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

#GLOBAL VARIABLES
BASE_FOLDER = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data"
RELEVANT_SIGNALS = {"breathing": ["BVP",], "pvt": ["HR",], "signature": ["ACC",], "transcription": ["ACC",], "drawing": ["ACC",], "tma": ["ACC",], "tmb": ["ACC",],  "tapping": ["HR",], "physical": ["ACC",]}

class MainWindow(tk.Frame):
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj

        self.title_font = Font(family = 'Helvetica', size = 20)
        self.text_font = Font(family = 'Helvetica', size = 16)
        
        self.counter = 0
        self.open_experiments = 0
        self.btn_list = [] #list to hold the button objects
        self.experiment_list = []

        #Layout
        tk.Frame.__init__(self, master)
        self.canvas = tk.Canvas(self.master, borderwidth = 0, background = "#ffffff")
        self.frame = tk.Frame(self.canvas, background = "#ffffff")
        self.vsb = tk.Scrollbar(self.master, orient = "vertical", command = self.canvas.yview)
        self.canvas.configure(yscrollcommand = self.vsb.set)

        self.vsb.pack(side = "right", fill = "y")
        self.canvas.pack(side = "left", fill = "both", expand = True)
        self.canvas.create_window((10,10), window = self.frame, anchor = "nw", tags = "self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.title_text = tk.StringVar()

        self.title_label = Label(self.frame, textvariable = self.title_text, font = self.title_font)

        self.first_button_text = StringVar()
        self.second_button_text = StringVar()

        self.first_button = Button(self.frame, textvar = self.first_button_text, font = self.text_font)
        self.second_button = Button(self.frame, textvar = self.second_button_text, font = self.text_font)

        self.home_button = Button(self.frame, text = "Home", command = self.initial_screen, font = self.text_font)

        self.initial_screen()

    def initial_screen(self):
        #Clear Screen
        self.clear_screen()
        self.first_button_text.set("Single experiments")
        self.second_button_text.set("All experiments")

        #Layout Screen
        self.title_text.set("Select an option")
        self.title_label.grid(row = 0, column = 0, sticky = "nsew")

        self.first_button['command'] = lambda option = 0: self.display_patients(option)
        self.second_button['command'] = lambda option = 1: self.display_patients(option)

        self.first_button.grid(row = 1, column = 0, sticky = "ew")
        self.second_button.grid(row = 2, column = 0, sticky = "ew")

        self.home_button.grid(row = 3, column = 0, sticky = "ew")
    
    def display_patients(self, option):
        self.clear_screen()

        self.title_text.set("Choose one patient")
        self.title_label.grid(row = 0, column = 0, sticky = "nswe")

        all_patients = self.db_obj.query_patients()

        for patient in all_patients:
            self.counter = self.counter + 1
            b = Button(self.frame, text = patient[0] + " - " + patient[1], command = lambda patient_id = patient[0]: self.selected_patients(patient_id, option), font = self.text_font)
            b.grid(row = self.counter, column = 0, sticky = "ew")
            self.btn_list.append(b)

        self.home_button.grid(row = self.counter + 1, column = 0, sticky = "ew")
    
    def selected_patients(self, patient_id, option):
        if option == 0:
            self.show_patient_experiments(patient_id)
        else:
            self.choose_mode(patient_id)
    
    def show_patient_experiments(self, patient_id):
        self.clear_screen()

        self.title_text.set("Choose one experiment")
        self.title_label.grid(row = 0, column = 0, sticky = "nsew")

        all_experiments = self.db_obj.query_patient_experiments(patient_id)
        for experiment in all_experiments:
            self.counter = self.counter + 1
            b = Button(self.frame, text = repr(experiment[0]), command = lambda experiment_number = experiment[0]: self.choose_mode(patient_id, experiment_number), font = self.text_font)
            b.grid(row = self.counter, column = 0, sticky = "w")
            self.btn_list.append(b)
        
        self.home_button.grid(row = self.counter + 1, column = 0, sticky = "ew")

    def choose_mode(self, *args):
        #args: patient_id, experiment_number (optional))
        self.clear_screen()
        
        self.title_text.set("Choose visualization mode")
        self.title_label.grid(row = 0, column = 0, sticky = "nsew")

        self.first_button_text.set("According to signal type")
        self.second_button_text.set("According to task")
        self.first_button['command'] = lambda: self.launch_new_window(*args, mode = "signal")
        self.second_button['command'] = lambda: self.launch_new_window(*args, mode = "task")
        self.first_button.grid(row = 1, column = 0, sticky = "ew")
        self.second_button.grid(row = 2, column = 0, sticky = "ew")

        self.home_button.grid(row = 3, column = 0, sticky = "ew")

    def launch_new_window(self, *args, mode):  
        #args -> patient_id, experiment_number (optional)
        window = Toplevel(self.master)
        patient_id = args[0]

        number_of_experiments = self.db_obj.get_experiment_number(patient_id)

        experiment_window = ExperimentObject(window, patient_id, mode, number_of_experiments)

        if len(args) == 2:
            experiment_number = args[1]
            experiment_window.one_experiment_layout(experiment_number)

        elif len(args) == 1:
            experiment_window.all_experiments_layout()

        #Configure row and column weights
        Grid.rowconfigure(window, 0, weight = 1)
        Grid.columnconfigure(window, 0, weight = 1)

        #Append new experiment window to list of open experiments
        self.experiment_list.append(experiment_window)

    def clear_screen(self):
        self.title_label.grid_forget()
        self.first_button.grid_forget()
        self.second_button.grid_forget()
        self.home_button.grid_forget()

        for b in self.btn_list[:]:
            self.counter = self.counter - 1
            b.grid_forget()
            self.btn_list.remove(b)
         
    def onFrameConfigure(self, event):
        #Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        
class ExperimentObject:
    def __init__(self, master, patient_id, mode, number_of_experiments):
        self.master = master
        self.title_font = Font(family = 'Helvetica', size = 20)
        self.text_font = Font(family = 'Helvetica', size = 16)

        self.patient_id = patient_id
        self.mode = mode
        self.number_of_experiments = number_of_experiments
        self.patient_folder = BASE_FOLDER + "\\" + self.patient_id

        #GUI Layout Widgets declaration
        self.super_frame = tk.Frame(self.master)
        self.super_frame.grid(row = 0, column = 0, sticky = "nswe")
        self.super_canvas = tk.Canvas(self.super_frame, width = self.master.winfo_screenwidth(), height = self.master.winfo_screenheight())
        #self.super_canvas.configure(scrollregion = self.super_canvas.bbox("all")) #Check if it is necessary
        self.y_scrollbar = tk.Scrollbar(self.super_frame, orient = "vertical")
        self.x_scrollbar = tk.Scrollbar(self.super_frame, orient = "horizontal")
        #Connect scrollbars to canvas
        self.y_scrollbar.configure(command = self.super_canvas.yview)
        self.x_scrollbar.configure(command = self.super_canvas.xview)
        self.super_canvas.configure(yscrollcommand = self.y_scrollbar.set)
        self.super_canvas.configure(xscrollcommand = self.x_scrollbar.set)

        self.super_frame.bind("<Configure>", self.onFrameConfigure)
        
        self.x_scrollbar.grid(row = 0, column = 0, sticky = "we")
        self.super_canvas.grid(row = 1, column = 0)
        self.y_scrollbar.grid(row = 1, column = 1, sticky = "ns")
        
        self.super_frame.rowconfigure(1, weight = 1)
        self.super_frame.columnconfigure(0, weight = 1)
        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)

    def one_experiment_layout(self, experiment_number):
        self.actual_experiment = experiment_number

        complete_folder = self.patient_folder + "\\" + repr(experiment_number)
        (e4_filename, json_filename) = self.get_files_name(complete_folder)
        
        empaticaObject = empaticaParser(complete_folder, e4_filename)
        timingsObject = timingsParser(complete_folder, json_filename, empaticaObject)

        #Call function to show one experiment and plot with coordinates 0,0
        display_columns = 2
        self.figure_agg = self.build_figure(empaticaObject, timingsObject, experiment_number, self.get_fig_size("single_experiment", self.mode), display_columns)
        self.super_canvas.create_window((0,0), window = self.figure_agg.get_tk_widget())
        
        #Code to make the figure appear
        self.master.bind("<Left>", self.leftKeyPressed)
        self.master.bind("<Right>", self.rightKeyPressed)

        self.super_canvas.configure(scrollregion = self.super_canvas.bbox("all"))
        self.super_canvas.grid(row = 1, column = 0)

    def all_experiments_layout(self):
        print("Develop code to build window showing all experiments")
        print(type(self.number_of_experiments), self.number_of_experiments)
        #Create for cycle and call function to show several experiments and plot with variable coordinates (calculated on the for)
        display_columns = 1
        
        #NUMBER OF GRAPHS PER SCREEN
        self.experiments_per_screen = 2.5
        

        for i in range(self.number_of_experiments):
            actual_experiment = i + 1
            
            complete_folder = self.patient_folder + "\\" + repr(actual_experiment)
            (e4_filename, json_filename) = self.get_files_name(complete_folder)

            empaticaObject = empaticaParser(complete_folder, e4_filename)
            timingsObject = timingsParser(complete_folder, json_filename, empaticaObject)
            
            self.figure_agg = self.build_figure(empaticaObject, timingsObject, actual_experiment, self.get_fig_size("all_experiments", self.mode), display_columns)
            self.super_canvas.create_window(( (i * (self.master.winfo_screenwidth()/self.experiments_per_screen) + 50) ,0), window = self.figure_agg.get_tk_widget())

            #Code to make the figure appear
            self.super_canvas.configure(scrollregion = self.super_canvas.bbox("all"))
            self.super_canvas.grid(row = 1, column = 0)

    def get_fig_size(self, option, mode):
        if option == "single_experiment":
            if mode == "signal":
                return (self.master.winfo_screenwidth()/100, 12)
            elif mode == "task":
                return (self.master.winfo_screenwidth()/100, 17)
            else:
                print("Error on get_fig_size() method. Didn't go to a predefined case - 1")

        elif option == "all_experiments":
            if mode == "signal":
                return (self.master.winfo_screenwidth()/(self.experiments_per_screen*100), 12)
            elif mode == "task":
                return (self.master.winfo_screenwidth()/(self.experiments_per_screen*100), 25)
            else:
                print("Error on get_fig_size() method. Didn't go to a predefined case - 2")
        else:
            print("Error on get_fig_size() method. Didn't go to a predefined case - 3")
    
    def build_figure(self, empaticaObject, timingsObject, experiment_number, figure_size, cols):
        #Builds the figure to be places on the Canvas
        width = figure_size[0]
        height = figure_size[1]
        figure = Figure(figsize = (figure_size[0], figure_size[1]))

        #if mode == signal -> self.master.winfo_screenwidth()/100, 9
        if self.mode == "signal":
            counter = 0

            for signal in empaticaObject.data.keys():
                if signal == "IBI":
                    continue
                    
                counter = counter + 1
                data = empaticaObject.data[signal]
                time, step = np.linspace(0, len(data)/SAMPLE_RATES[signal], num = len(data), endpoint = False, retstep = True)

                new_figure = figure.add_subplot(int("51" + repr(counter)))
                new_figure.plot(time, data)
                new_figure.set_xlabel("Time in Seconds")
                new_figure.set_ylabel(signal)
        
        #if mode == task  self.master.winfo_screenwidth()/100, 17
        elif self.mode == "task":
            counter = 0
            
            if cols == 1:
                rows = 9
            elif cols == 2:
                rows = 5

            for exercise in timingsObject.exercise_indexes.keys():
                for signal in RELEVANT_SIGNALS[exercise]:
                    if signal == "HR":
                        continue

                    counter = counter + 1
                    start_index = timingsObject.exercise_indexes[exercise][signal]['start_index']
                    end_index = timingsObject.exercise_indexes[exercise][signal]['end_index']
                    data = empaticaObject.data[signal][start_index:end_index]
                    
                    new_figure = figure.add_subplot(rows, cols, counter)
                    new_figure.plot(data)
                    #new_figure.set_xlabel("Samples")
                    new_figure.set_ylabel(signal)
                    new_figure.set_title(exercise)

        
        #Build FigureCanvasTkAgg object and return it, to be drawn on the canvas
        figure.suptitle("Patient " + self.patient_id + " - Experiment " + repr(experiment_number))
        figure.set_tight_layout(True)
        figure_agg = FigureCanvasTkAgg(figure, self.super_canvas)
        figure_agg.draw()

        return figure_agg

    def get_files_name(self, experiment_folder):
        (e4_file, json_file) = (None, None)

        for file in os.listdir(experiment_folder):
            if file.endswith(".zip"):
                e4_file = file
            elif file.endswith(".json"):
                if "correcao" not in file:
                    json_file = file

        if e4_file == None or json_file == None:
            print("Error: There is no E4 or JSON file for patient " + self.patient_id + " in experiment " + repr(self.experiment_number))
            return (None, None)
            
        if len(os.listdir(experiment_folder)) < 4: #Usually there are 2 files, but it's possible to have 3 if a correction to the experiment was needed
            zip = zipfile.ZipFile(experiment_folder + "\\" + e4_file, 'r')
            zip.extractall(experiment_folder)

        return (e4_file, json_file)
    
    def onFrameConfigure(self, event):
        #Reset the scroll region to encompass the inner frame
        self.super_canvas.configure(scrollregion = self.super_canvas.bbox("all"))
    
    def leftKeyPressed(self, event):
        #When left key is pressed, display previous experiment
         if self.actual_experiment != 1:
            exp = self.actual_experiment - 1
            self.figure_agg.get_tk_widget().destroy()
            self.one_experiment_layout(exp)
    
    def rightKeyPressed(self, event):
        #When right key is pressed, display next experiment
        if self.actual_experiment != self.number_of_experiments:
            exp = self.actual_experiment + 1
            self.figure_agg.get_tk_widget().destroy()
            self.one_experiment_layout(exp)



# class ShowExperiment:
#     def __init__(self, master, patient_id):
#         self.master = master
#         self.title_font = Font(family = 'Helvetica', size = 20)
#         self.text_font = Font(family = 'Helvetica', size = 16)

#         self.patient_id = patient_id
#         self.patient_folder = BASE_FOLDER + "\\" + self.patient_id

#         #GUI Layout Widgets declaration
#         self.super_frame = tk.Frame(self.master)
#         self.super_frame.grid(row = 0, column = 0, sticky = "nswe")

#         self.canvas_width = self.master.winfo_screenwidth()
#         self.canvas_height = self.master.winfo_screenheight()
#         self.super_canvas = tk.Canvas(self.super_frame, width = self.canvas_width, height = self.canvas_height)
#         #self.super_canvas.configure(scrollregion = self.super_canvas.bbox("all")) #Check if it is necessary

#         self.y_scrollbar = tk.Scrollbar(self.super_frame, orient = "vertical")
#         self.x_scrollbar = tk.Scrollbar(self.super_frame, orient = "horizontal")
#         self.y_scrollbar.configure(command = self.super_canvas.yview)
#         self.x_scrollbar.configure(command = self.super_canvas.xview)
#         self.super_canvas.configure(yscrollcommand = self.y_scrollbar.set)
#         self.super_canvas.configure(xscrollcommand = self.x_scrollbar.set)

#         self.x_scrollbar.grid(row = 0, column = 0, sticky = "we")
#         self.super_canvas.grid(row = 1, column = 0)
#         self.y_scrollbar.grid(row = 1, column = 1, sticky = "ns")
        
#         self.super_frame.rowconfigure(1, weight = 1)
#         self.super_frame.columnconfigure(0, weight = 1)
#         self.master.rowconfigure(0, weight = 1)
#         self.master.columnconfigure(0, weight = 1)

#         self.super_frame.bind("<Configure>", self.onFrameConfigure)
    
#     def 

#     def display_all_experiments(self):
#         plt.figure(figsize = (5 * self.number_experiments, 10))
#         for i in range(self.number_experiments):
#             experiment_folder = self.patient_folder + "\\" + repr(i+1)

#             (e4_file, json_file) = self.get_files_name(self.patient_folder, i + 1)
#             empaticaObject = empaticaParser(experiment_folder, e4_file)
#             timingsObject = timingsParser(experiment_folder, json_file, empaticaObject)

#             self.display_experiment(i, empaticaObject, timingsObject)
#             #self.simple_experiment_plot(i, empaticaObject, timingsObject)
            
#         #plt.show()
    
#     def display_experiment_alternative(self, index_experiment, empaticaObject, timingsObject):
#         counter = 0
#         actual_experiment = index_experiment + 1

#         for signal in empaticaObject.data.keys():
#             if signal == "IBI":
#                 continue
            
#             data = empaticaObject.data[signal]

#             index = self.get_row_column_position_alternative(self.number_experiments, actual_experiment, counter)
#             new_figure = self.alternative_figure.add_subplot(5, self.number_experiments, index)
#             new_figure.plot(data)
#             new_figure.set_xlabel("Samples")
#             new_figure.set_ylabel(signal)

#             counter = counter + 1
            
#         #figure.suptitle("Experiment " + repr(actual_experiment)

#         if actual_experiment == self.number_experiments:
#             figure_agg = FigureCanvasTkAgg(self.alternative_figure, self.super_canvas)
#             figure_agg.draw()
            
#             self.super_canvas.create_window((0,0), window = figure_agg.get_tk_widget())

#             #self.canvas_list.append(canvas)
#             #self.figure_list.append(figure)
#             self.figure_agg_list.append(figure_agg)
    
#     def get_row_column_position_alternative(self, total_experiments, actual_experiment, signal_counter):
#         index = actual_experiment + (signal_counter) * total_experiments
        
#         return index

#     def get_row_column_position(self, index_experiment):
#         row = 1
#         column = index_experiment + 1
        
#         return (row, column)

#     def display_experiment(self, index_experiment, empaticaObject, timingsObject):
#         counter = 0
#         canvas = tk.Canvas(self.super_canvas) #can define size later
#         figure = Figure(figsize = (5.5,8))
#         width = 500

#         for signal in empaticaObject.data.keys():
#             if signal == "IBI":
#                 continue
            
#             counter = counter + 1

#             data = empaticaObject.data[signal]
#             (tempo, step) = np.linspace(0, len(data)/SAMPLE_RATES[signal], num = len(data), endpoint = False, retstep = True)

#             new_figure = figure.add_subplot(int("51" + repr(counter)))
#             new_figure.plot(tempo, data)
#             new_figure.set_xlabel("Samples")
#             new_figure.set_ylabel(signal)

#         figure.suptitle("Experiment " + repr(index_experiment + 1))

#         figure_agg = FigureCanvasTkAgg(figure, self.super_canvas)
#         figure_agg.draw()

#         (pos_row, pos_column) = self.get_row_column_position(index_experiment)
#         self.super_canvas.create_window((10*(index_experiment + 1) + (width*index_experiment), 50), window = figure_agg.get_tk_widget(), anchor = "nw")

#         self.canvas_list.append(canvas)
#         self.figure_list.append(figure)
#         self.figure_agg_list.append(figure_agg)
    
#     def show_all_tasks(self):
#         print("Code to plot all tasks")
    
#     def show_experiment_tasks(self):
#         print("Code to plot experiment tasks")
    
#     def get_files_name(self, patient_folder, experiment_number):
#         experiment_folder = patient_folder + "\\" + repr(experiment_number)
        
#         (e4_file, json_file) = (None, None)

#         for file in os.listdir(experiment_folder):
#             if file.endswith(".zip"):
#                 e4_file = file
#             elif file.endswith(".json"):
#                 if "correcao" not in file:
#                     json_file = file

#         if e4_file == None or json_file == None:
#             print("Error: There is no E4 or JSON file for patient " + self.patient_id + " in experiment " + repr(self.experiment_number))
#             return (None, None)
            
#         if len(os.listdir(experiment_folder)) < 4: #Usually there are 2 files, but it's possible to have 3 if a correction to the experiment was needed
#             zip = zipfile.ZipFile(experiment_folder + "\\" + e4_file, 'r')
#             zip.extractall(experiment_folder)

#         return (e4_file, json_file)

#     def simple_experiment_plot(self, index_experiment, empaticaObject, timingsObject):
#         counter = 0

#         actual_experiment = index_experiment + 1
#         for signal in empaticaObject.data.keys():
#             if signal == "IBI":
#                 continue
            
          
#             data = empaticaObject.data[signal]
#             index = actual_experiment + counter * self.number_experiments
            
#             plt.subplot(5, self.number_experiments, index)
#             plt.title(signal)
#             plt.plot(data)

#             counter = counter + 1
            
#     def onFrameConfigure(self, event):
#         self.super_canvas.configure(scrollregion = self.super_canvas.bbox("all"))


if __name__ == "__main__":
    #Database functions
    db_obj = DatabaseObject()
    db_obj.create_patient_table()
    db_obj.create_session_table()

    #Graphical Interface Functions
    root = tk.Tk()
    Grid.rowconfigure(root, 0, weight = 1)
    Grid.columnconfigure(root, 0, weight = 1)

    MainWindow(root, db_obj).pack(side = "top", fill = "both", expand = True)
    root.mainloop()