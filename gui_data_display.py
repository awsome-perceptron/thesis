from separation_indexes_calculation import empaticaParser, timingsParser, panasParser, completeSession, SAMPLE_RATES, unitTesting
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
        self.third_button_text = StringVar()
        self.fourth_button_text = StringVar()

        self.first_button = Button(self.frame, textvar = self.first_button_text, font = self.text_font)
        self.second_button = Button(self.frame, textvar = self.second_button_text, font = self.text_font)
        self.third_button = Button(self.frame, textvar = self.third_button_text, font = self.text_font)
        self.fourth_button = Button(self.frame, textvar = self.fourth_button_text, font = self.text_font)

        self.home_button = Button(self.frame, text = "Home", command = self.display_patients, font = self.text_font)

        self.display_patients()
    
    def display_patients(self):
        self.clear_screen()

        self.title_text.set("Choose one patient")
        self.title_label.grid(row = 0, column = 0, sticky = "nswe")

        all_patients = self.db_obj.query_patients()

        for patient in all_patients:
            self.counter = self.counter + 1
            b = Button(self.frame, text = patient[0] + " - " + patient[1], command = lambda patient_id = patient[0]: self.display_options(patient_id), font = self.text_font)
            b.grid(row = self.counter, column = 0, sticky = "ew")
            self.btn_list.append(b)

        self.home_button.grid(row = self.counter + 1, column = 0, sticky = "ew")

    def display_options(self, patient_id):
        self.clear_screen()

        self.title_text.set("Select an option")
        self.title_label.grid(row = 0, column = 0, sticky = "nswe")

        self.first_button_text.set("Inspect an experiment")
        self.first_button['command'] = lambda: self.selected_option(patient_id, option = "one_experiment")

        self.second_button_text.set("Compare experiments")
        self.second_button['command'] = lambda: self.selected_option(patient_id, option = "all_experiments")

        self.first_button.grid(row = 1, column = 0, sticky = "ew")
        self.second_button.grid(row = 2, column = 0, sticky = "ew")

        self.home_button.grid(row = 3, column = 0, sticky = "ew")

    def selected_option(self, patient_id, option):
        if option == "one_experiment":
            self.show_patient_experiments(patient_id, option)

        elif option == "all_experiments":
            self.choose_visualization_mode(patient_id, option)

    def show_patient_experiments(self, patient_id, option):
        self.clear_screen()

        self.title_text.set("Choose one experiment")
        self.title_label.grid(row = 0, column = 0, sticky = "nsew")

        all_experiments = self.db_obj.query_patient_experiments(patient_id)

        for experiment in all_experiments:
            self.counter = self.counter + 1
            b = Button(self.frame, text = repr(experiment[0]), command = lambda experiment_number = experiment[0]: self.choose_visualization_mode(patient_id, option, experiment_number), font = self.text_font)
            b.grid(row = self.counter, column = 0, sticky = "w")
            self.btn_list.append(b)
        
        self.home_button.grid(row = self.counter + 1, column = 0, sticky = "ew")

    def choose_visualization_mode(self, *args):
        #args: patient_id, experiment_number (optional))
        self.clear_screen()
        
        self.title_text.set("Choose visualization mode")
        self.title_label.grid(row = 0, column = 0, sticky = "nsew")

        self.first_button_text.set("Raw signals")
        self.second_button_text.set("Task relevant signals")
        self.third_button_text.set("Raw signals detrended")
        self.fourth_button_text.set("Task relevant signals detrended")

        self.first_button['command'] = lambda: self.launch_new_window(*args, view_mode = "raw_signals")
        self.second_button['command'] = lambda: self.launch_new_window(*args, view_mode = "task_signals")
        self.third_button['command'] = lambda: self.launch_new_window(*args, view_mode = "raw_signals_detrended")
        self.fourth_button['command'] = lambda: self.launch_new_window(*args, view_mode = "task_signals_detrended")

        self.first_button.grid(row = 1, column = 0, sticky = "ew")
        self.second_button.grid(row = 2, column = 0, sticky = "ew")
        self.third_button.grid(row = 3, column = 0, sticky = "ew")
        self.fourth_button.grid(row = 4, column = 0, sticky = "ew")

        self.home_button.grid(row = 5, column = 0, sticky = "ew")

    def launch_new_window(self, *args, view_mode):  
        #args: [0] -> patient_id | [1] -> option (one_experiment or all_experiments) | [2] (optional) -> experiment_number
        patient_id = args[0]
        option = args[1]
        total_experiments = self.db_obj.get_experiment_number(patient_id)

        window = Toplevel(self.master)
        experiment_window = ExperimentObject(window, patient_id, total_experiments)

        if option == "one_experiment":
            experiment_number = args[2]
            experiment_window.one_experiment_layout(experiment_number, view_mode)

        elif option == "all_experiments":
            experiment_window.all_experiments_layout(view_mode)

        #Configure row and column weights
        Grid.rowconfigure(window, 0, weight = 1)
        Grid.columnconfigure(window, 0, weight = 1)

        #Append new experiment window to list of open experiments
        self.experiment_list.append(experiment_window)

    def clear_screen(self):
        self.title_label.grid_forget()

        self.first_button.grid_forget()
        self.second_button.grid_forget()
        self.third_button.grid_forget()
        self.fourth_button.grid_forget()

        self.home_button.grid_forget()

        for b in self.btn_list[:]:
            self.counter = self.counter - 1
            b.grid_forget()
            self.btn_list.remove(b)
         
    def onFrameConfigure(self, event):
        #Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        
class ExperimentObject:
    def __init__(self, master, patient_id, number_of_experiments):
        self.master = master
        self.title_font = Font(family = 'Helvetica', size = 20)
        self.text_font = Font(family = 'Helvetica', size = 16)

        self.patient_id = patient_id
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

    def one_experiment_layout(self, experiment_number, view_mode):
        self.actual_experiment = experiment_number
        self.view_mode = view_mode

        complete_folder = self.patient_folder + "\\" + repr(experiment_number)
        (e4_filename, json_filename) = self.get_files_name(complete_folder)
        
        empaticaObject = empaticaParser(complete_folder, e4_filename)
        timingsObject = timingsParser(complete_folder, json_filename, empaticaObject)
        panasObject = panasParser(complete_folder)

        sessionObject = completeSession(empaticaObject, timingsObject, panasObject)

        if view_mode == "task_signals_detrended" or view_mode == "raw_signals_detrended":
            data = sessionObject.empaticaObject.data_detrended
        else:
            data = sessionObject.empaticaObject.data

        #Call function to show one experiment and plot with coordinates 0,0
        self.figure_agg = self.build_figure(data, timingsObject.exercise_indexes, experiment_number, self.get_layout_dimensions("one_experiment", view_mode), view_mode)
        self.super_canvas.create_window((0,0), window = self.figure_agg.get_tk_widget())
        
        #Code to make the figure appear, and append left and right keys to next experiment
        self.master.bind("<Left>", self.leftKeyPressed)
        self.master.bind("<Right>", self.rightKeyPressed)

        self.super_canvas.configure(scrollregion = self.super_canvas.bbox("all"))
        self.super_canvas.grid(row = 1, column = 0)
            
        #Call unit tests here
        self.callUnitTests(sessionObject)

    
    def all_experiments_layout(self, view_mode):
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
            panasObject = panasParser(complete_folder)

            sessionObject = completeSession(empaticaObject, timingsObject, panasObject)

            if view_mode == "task_signals_detrended" or view_mode == "raw_signals_detrended":
                data = sessionObject.empaticaObject.data_detrended
            else:
                data = sessionObject.empaticaObject.data
            
            self.figure_agg = self.build_figure(data, timingsObject.exercise_indexes, actual_experiment, self.get_layout_dimensions("all_experiments", view_mode), view_mode)
            self.super_canvas.create_window(( (i * (self.master.winfo_screenwidth()/self.experiments_per_screen) + 50) ,0), window = self.figure_agg.get_tk_widget())

            #Code to make the figure appear
            self.super_canvas.configure(scrollregion = self.super_canvas.bbox("all"))
            self.super_canvas.grid(row = 1, column = 0)

            #Call unit tests here
            self.callUnitTests(sessionObject)

    def get_layout_dimensions(self, option, view_mode):
        if option == "one_experiment":
            if view_mode == "raw_signals" or view_mode == "raw_signals_detrended":
                return (self.master.winfo_screenwidth()/100, 12, 5, 1)
            elif view_mode == "task_signals" or view_mode == "task_signals_detrended":
                return (self.master.winfo_screenwidth()/100, 17, 5, 2)
            else:
                print("Error on get_fig_size() method. Didn't go to a predefined case - 1")

        elif option == "all_experiments":
            if view_mode == "raw_signals" or view_mode == "raw_signals_detrended":
                return (self.master.winfo_screenwidth()/(self.experiments_per_screen*100), 12, 5, 1)
            elif view_mode == "task_signals" or view_mode == "task_signals_detrended":
                return (self.master.winfo_screenwidth()/(self.experiments_per_screen*100), 25, 9, 1)
            else:
                print("Error on get_fig_size() method. Didn't go to a predefined case - 2")
        else:
            print("Error on get_fig_size() method. Didn't go to a predefined case - 3")
    
    def build_figure(self, data_dictionary, exercise_indexes_dictionary, experiment_number, layout_dimensions, view_mode):
        #Builds the figure to be places on the Canvas
        subplot_width = layout_dimensions[0]
        subplot_height = layout_dimensions[1]
        number_rows = layout_dimensions[2]
        number_cols = layout_dimensions[3]

        figure = Figure(figsize = (subplot_width, subplot_height))

        #if mode == signal -> self.master.winfo_screenwidth()/100, 9
        if view_mode == "raw_signals" or view_mode == "raw_signals_detrended":
            counter = 0

            for signal in data_dictionary.keys():
                if signal == "IBI":
                    continue
                    
                counter = counter + 1
                data = data_dictionary[signal]
                time, step = np.linspace(0, len(data)/SAMPLE_RATES[signal], num = len(data), endpoint = False, retstep = True)
                #51counter
                new_figure = figure.add_subplot(number_rows, number_cols, counter)
                new_figure.plot(time, data)

                if signal == "ACC":
                    legend = new_figure.legend(['X', 'Y', 'Z', 'Magnitude'], loc = 'upper right')


                new_figure.set_xlabel("Time in Seconds")
                new_figure.set_ylabel(signal)

        
        #if mode == task  self.master.winfo_screenwidth()/100, 17
        elif view_mode == "task_signals" or view_mode == "task_signals_detrended":
            counter = 0

            for exercise in exercise_indexes_dictionary.keys():
                for signal in RELEVANT_SIGNALS[exercise]:
                    if signal == "HR":
                        continue

                    counter = counter + 1
                    start_index = exercise_indexes_dictionary[exercise][signal]['start_index']
                    end_index = exercise_indexes_dictionary[exercise][signal]['end_index']
                    data_slice = data_dictionary[signal][start_index:end_index]
                    
                    new_figure = figure.add_subplot(number_rows, number_cols, counter)
                    new_figure.plot(data_slice)
                    legend = new_figure.legend(['X', 'Y', 'Z'], loc = 'upper right')
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
                if "correcao" not in file and "panas" not in file:
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
            self.one_experiment_layout(exp, self.view_mode)
    
    def rightKeyPressed(self, event):
        #When right key is pressed, display next experiment
        if self.actual_experiment != self.number_of_experiments:
            exp = self.actual_experiment + 1
            self.figure_agg.get_tk_widget().destroy()
            self.one_experiment_layout(exp, self.view_mode)

    def callUnitTests(self, sessionObject):
        unitTests = unitTesting(sessionObject)
        #unitTests.actigraphy_means_dictionary()

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