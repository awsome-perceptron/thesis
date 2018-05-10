from separation_indexes_calculation import empaticaParser, timingsParser, SAMPLE_RATES
from patient_gui_interface import DatabaseObject
import sqlite3
from tkinter import *
import tkinter as tk
from tkinter.font import Font
import os
import zipfile

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

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
        self.title_text.set("Select one patient")
        self.title_label = Label(self.frame, textvariable = self.title_text, font = self.title_font)
        self.title_label.grid(row = self.counter, column = 0, sticky = "nswe")

        self.back_button = Button(self.frame, text = "Back", font = self.text_font)

        self.show_patients()
        
    def show_patients(self):
        #Fetch data from database
        all_patients = self.db_obj.query_patients()

        self.back_button.grid_forget()
        self.back_button['command'] = None

        self.title_text.set("Select one patient")

        for b in self.btn_list[:]:
            self.counter = self.counter - 1
            b.grid_forget()
            self.btn_list.remove(b)

        for patient in all_patients:
            self.counter = self.counter + 1
            b = Button(self.frame, text = patient[0] + " - " + patient[1], command = lambda patient_id = patient[0]: self.show_patient_experiments(patient_id), font = self.text_font)
            b.grid(row = self.counter, column = 0, sticky = "w")

            self.btn_list.append(b) #append button to button list

        self.back_button.grid(row = self.counter + 1, column = 0, sticky = "nswe")

    def show_patient_experiments(self, patient_id):
        all_experiments = self.db_obj.query_patient_experiments(patient_id)

        self.back_button.grid_forget()
        self.back_button['command'] = self.show_patients

        for b in self.btn_list[:]:
            self.counter = self.counter - 1
            b.grid_forget()
            self.btn_list.remove(b)

        self.title_text.set("Patient " + patient_id + " - Select an experiment")

        for experiment in all_experiments:
            self.counter = self.counter + 1
            b = Button(self.frame, text = repr(experiment[0]), command = lambda experiment_number = experiment[0]: self.show_options(patient_id, experiment_number), font = self.text_font)
            b.grid(row = self.counter, column = 0, sticky = "w")

            self.btn_list.append(b)

        self.back_button.grid(row = self.counter + 1, column = 0, sticky = "nswe")

    def show_options(self, patient_id, experiment_number):
        for b in self.btn_list[:]:
            self.counter = self.counter - 1
            b.grid_forget()
            self.btn_list.remove(b)
        
        self.title_text.set("Choose a display option")
        option_1 = tk.Button(self.frame, text = "Show Complete Data", command = lambda option = 0: self.display_experiment(patient_id, experiment_number, option), font = self.text_font)
        option_1.grid(row = 1, column = 0, sticky = "w")

        option_2 = tk.Button(self.frame, text = "Show Task Data", command = lambda option = 1: self.display_experiment(patient_id, experiment_number, option), font = self.text_font)
        option_2.grid(row = 2, column = 0, sticky = "w")

        self.btn_list.append(option_1)
        self.btn_list.append(option_2)

        self.counter = self.counter + 2

    def display_experiment(self, patient_id, experiment_number, option):
        #Launch new window
        self.open_experiments = self.open_experiments + 1

        window = Toplevel(self.master)
        experiment = ExperimentDisplay(window, patient_id, experiment_number, option)

        self.experiment_list.append(experiment)

    def onFrameConfigure(self, event):
        #Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        

class ExperimentDisplay:
    def __init__(self, master, patient_id, experiment_number, option):
        self.master = master
        self.patient_id = patient_id
        self.experiment_number = experiment_number
        self.folder = BASE_FOLDER + "\\" + self.patient_id + "\\" + repr(self.experiment_number)

        self.title_font = Font(family = 'Helvetica', size = 20)
        self.text_font = Font(family = 'Helvetica', size = 16)

        self.frame = tk.Frame(self.master)
        self.frame.grid(row = 0, column = 0, sticky = "nswe")

        self.master.rowconfigure(0, weight = 1)
        self.master.columnconfigure(0, weight = 1)

        self.figure = Figure(figsize = (8,10), dpi = 100)

        self.fetch_filenames()
        self.empaticaObject = empaticaParser(self.folder, self.e4_file)
        self.timingsObject = timingsParser(self.folder, self.json_file, self.empaticaObject)

        if option == 0:
            self.plot_complete_data()
        elif option == 1:
            self.plot_task_data()

        self.scrollingFigure()

    def addScrollingFigure(self):
        self.canvas = tk.Canvas(self.frame)
        self.canvas.grid(row = 1, column = 1, sticky = "nsew")

        self.xScrollBar = tk.Scrollbar(self.frame, orient = "horizontal")
        self.yScrollBar = tk.Scrollbar(self.frame)

        self.xScrollBar.grid(row = 2, column = 1, sticky = "ew")
        self.yScrollBar.grid(row = 1, column = 2, sticky = "ns")

        self.canvas.config(xscrollcommand = self.xScrollBar.set)
        self.xScrollBar.config(command = self.canvas.xview)
        self.canvas.config(yscrollcommand = self.yScrollBar.set)
        self.yScrollBar.config(command = self.canvas.yview)
        
        self.figAgg = FigureCanvasTkAgg(self.figure, self.canvas)
        self.mplCanvas = self.figAgg.get_tk_widget()

        self.cwid = self.canvas.create_window(0, 0, window = self.mplCanvas, anchor = "nw")

    def fetch_filenames(self):
        self.e4_file = None
        self.json_file = None
        complete_folder = BASE_FOLDER + "\\" + self.patient_id + "\\" + repr(self.experiment_number)

        for file in os.listdir(complete_folder):
            if file.endswith(".zip"):
                self.e4_file = file
            elif file.endswith(".json"):
                self.json_file = file

        if self.e4_file == None or self.json_file == None:
            print("Error: There is no E4 or JSON file for patient " + self.patient_id + " in experiment " + repr(self.experiment_number))
            
        if len(os.listdir(complete_folder)) < 4: #Usually there are 2 files, but it's possible to have 3 if a correction to the experiment was needed
            zip = zipfile.ZipFile(complete_folder + "\\" + self.e4_file, 'r')
            zip.extractall(complete_folder)
        
    def plot_complete_data(self):
        counter = 0
        for signal in self.empaticaObject.data.keys():
            if signal == "IBI":
                continue

            data = self.empaticaObject.data[signal]
            (time_scale, step) = np.linspace(0, len(data)/SAMPLE_RATES[signal], num = len(data), endpoint = False, retstep = True, dtype = float)
            
            print("Len: " + repr(len(time_scale)) + " | step: " + repr(step))
            counter = counter + 1
            new_figure = self.figure.add_subplot(int("61" + repr(counter)))
            new_figure.plot(time_scale, data)
            new_figure.set_xlabel("Time")
            new_figure.set_ylabel(signal)

    def plot_task_data(self):
        counter = 0
    
    
    def scrollingFigure(self):
        self.canvas = tk.Canvas(self.frame)
        self.canvas.grid(row = 0, column = 0, sticky = "nswe")

        self.xBar = tk.Scrollbar(self.frame, orient = "horizontal")
        self.yBar = tk.Scrollbar(self.frame, orient = "vertical")

        self.xBar.grid(row = 1, column = 0, sticky = "ew")
        self.yBar.grid(row = 0, column = 1, sticky = "ns")

        self.frame.rowconfigure(0, weight = 1)
        self.frame.columnconfigure(0, weight = 1)

        self.canvas.config(xscrollcommand = self.xBar.set)
        self.xBar.config(command = self.canvas.xview)
        self.canvas.config(yscrollcommand = self.yBar.set)
        self.yBar.config(command= self.canvas.yview)

        #plug the figure
        self.figAgg = FigureCanvasTkAgg(self.figure, self.canvas)
        self.mplCanvas = self.figAgg.get_tk_widget()
        self.mplCanvas.grid(row = 1, column = 0, sticky = "nswe")

        #and connect figure with scrolling region
        self.canvas.create_window(0, 0, window = self.mplCanvas)
        self.canvas.config(scrollregion = self.canvas.bbox("all"))

        

#GLOBAL VARIABLES
BASE_FOLDER = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data"

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