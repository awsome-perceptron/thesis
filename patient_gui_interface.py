from tkinter import filedialog
from tkinter import *
from tkinter.font import Font
import sqlite3
import time
from shutil import copy, move
import os

#database functions
class DatabaseObject:
    def __init__(self):
        self.db = sqlite3.connect('my_database')
        self.create_patient_table()

    def close_db_connection(self):
        self.db.close()

    def create_patient_table(self):
        cursor = self.db.cursor()
        sql = '''CREATE TABLE IF NOT EXISTS patient(id TEXT PRIMARY KEY, name TEXT, insertion_epoch INTEGER)'''
        cursor.execute(sql)
        self.db.commit()       

    def create_session_table(self):
        cursor = self.db.cursor()
        sql = '''CREATE TABLE IF NOT EXISTS session(number INTEGER, session_name TEXT,
        patient_id TEXT, timings_name TEXT,  
        PRIMARY KEY(number,patient_id),
        FOREIGN KEY(patient_id) REFERENCES patient(id)
        )'''
        cursor.execute(sql)
        self.db.commit()

    def drop_table(self, table_name):
        cursor = self.db.cursor()
        sql = "DROP TABLE IF EXISTS " + table_name
        cursor.execute(sql)
        self.db.commit()

    def insert_patient(self, p_id, p_name):
        p_epoch = int(time.time())
        cursor = self.db.cursor()
        sql = '''INSERT INTO patient(id, name, insertion_epoch) VALUES(?,?,?)'''
        cursor.execute(sql, (p_id, p_name, p_epoch))
        print("User " + p_name + " inserted!")
        self.db.commit()

    def insert_session(self, number, session_name, patient_id, timings_name):
        cursor = self.db.cursor()
        sql = '''INSERT INTO session(number, session_name, patient_id, timings_name) VALUES (?,?,?,?)'''
        cursor.execute(sql, (number, session_name, patient_id, timings_name))
        print("Session " + repr(number) + " from " + patient_id + " inserted!")
        self.db.commit()

    def display_patients(self):
        cursor = self.db.cursor()
        cursor.execute('''SELECT id, name FROM patient''')
        all_rows = cursor.fetchall()
        print(" - - - - - - - - - - - - - - - - - - Display of Patients - - - - - - - - - - - - - - - - - -")
        for row in all_rows:
            print('ID: {0}, NAME: {1}'.format(row[0],row[1]))
    
    def display_sessions(self):   
        cursor = self.db.cursor()
        cursor.execute('''SELECT number, patient_id
                        FROM session''')
        all_rows = cursor.fetchall()
        for row in all_rows:
            print('ID:{1}, #EXP:{0}'.format(row[0],row[1]))

    def populate_tables(self):
        self.insert_patient("H1", "Rita Oliveira")
        self.insert_patient("H_INV", "John Doe")

        self.insert_session(1, "1656545646_DEVICE_SNUM", "H1", "TIMINGS_FILE_NAME")
        self.insert_session(2, "165654456456_DEVICE_SNUM", "H1", "TIMINGS_FILE_NAME")
        self.insert_session(3, "16565456456_DEVICE_SNUM", "H1", "TIMINGS_FILE_NAME")

        self.insert_session(1, "165654566456_DEVICE_SNUM", "H_INV", "TIMINGS_FILE_NAME")
        self.insert_session(2, "1656545646456_DEVICE_SNUM", "H_INV", "TIMINGS_FILE_NAME")

    def query_patients(self):
        cursor = self.db.cursor()
        cursor.execute('''SELECT id, name FROM patient''')
        all_rows = cursor.fetchall()

        return all_rows

    def drop_all_tables(self):
        self.drop_table("patient")
        self.drop_table("session")

    def get_experiment_number(self, pat_id):
        cursor = self.db.cursor()
        cursor.execute('''SELECT MAX(number) FROM session WHERE patient_id = ?
                        ''', (pat_id,))
        
        result = cursor.fetchone()[0]
        if result:
            return int(result)
        else:
            return 0

#CLASSES FOR GUI INTERFACE

class MainWindow:
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj
        self.frame = Frame(self.master)
        self.bottom_frame = Frame(self.master)

        self.helv36 = Font(family = 'Helvetica', size = 36)

        self.button_patient = Button(self.frame, text = "PATIENT", fg = "white", bg = "grey", font = self.helv36)
        self.button_patient['command'] = lambda: self.open_patient_window()
        self.button_patient.pack(fill = "both", expand = "yes")

        self.button_experiment = Button(self.bottom_frame, text = "EXPERIMENT", fg = "white", bg = "grey", font = self.helv36)
        self.button_experiment['command'] = lambda: self.open_experiment_window()
        self.button_experiment.pack(fill = "both", expand = "yes")

        self.frame.pack(fill = "both", expand = "yes")
        self.bottom_frame.pack(fill = "both", expand = "yes")
    
    def open_patient_window(self):
        self.window_1 = Toplevel(self.master)
        self.patient_window = PatientWindow(self.window_1, self.db_obj)
    
    def open_experiment_window(self):
        self.window_2 = Toplevel(self.master)
        self.experiment_window = ExperimentWindow(self.window_2, self.db_obj)

class PatientWindow:
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj

        self.title_font = Font(family = 'Helvetica', size = 26)
        self.text_font = Font(family = 'Helvetica', size = 16)
        
        self.frame = Frame(self.master)

        self.title = Label(self.frame, text = "Create new patient", font = self.text_font)
        self.title.grid(row = 0, column = 0, sticky = "nsew", columnspan = 2)

        Label(self.frame, text = "Patient name", font = self.text_font).grid(row = 1, column = 0, sticky = "w")
        Label(self.frame, text = "Patient ID", font = self.text_font).grid(row = 2, column = 0, sticky = "w")

        self.name_entry = Entry(self.frame)
        self.id_entry = Entry(self.frame)

        self.name_entry.grid(row = 1, column = 1)
        self.id_entry.grid(row = 2, column = 1)

        self.button_submit = Button(self.frame, text = "Submit", command = self.submit_method, font = self.text_font)
        self.button_submit.grid(row = 3, column = 0)

        self.button_quit = Button(self.frame, text = "Quit", command = self.close_window, font = self.text_font)
        self.button_quit.grid(row = 3, column = 1)

        self.button_display = Button(self.frame, text = "Display", command = self.display_patients, font = self.text_font)
        self.button_display.grid(row = 4, column = 0)

        self.frame.grid(row = 0, column = 0, sticky = "nesw")
    
    def display_patients(self):
        self.db_obj.display_patients()

    def submit_method(self):
        name = self.name_entry.get()
        id_ = self.id_entry.get()

        if len(name) == 0 or len(id_) == 0:
            print("Error: Name or ID field is empty!")
            return 

        self.name_entry.delete(0, 'end')
        self.id_entry.delete(0, 'end')

        self.db_obj.insert_patient(id_, name)

        #create folder for new patient

        folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\" + id_
        
        #create directory and move files
        os.makedirs(folder)
        

    def close_window(self):
        self.master.destroy()

class ExperimentWindow:
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj
        self.counter = 0

        self.btn_list = [] #list to hold the button objects

        self.title_font = Font(family = 'Helvetica', size = 26)
        self.text_font = Font(family = 'Helvetica', size = 16)
        
        self.frame = Frame(self.master)

        self.title_text = StringVar()
        self.title_text.set("New experiment: Click on the patient")

        self.title = Label(self.frame, textvariable = self.title_text, font = self.text_font)
        self.title.grid(row = 0, column = 0, sticky = "nsew")

        all_patients = self.db_obj.query_patients()

        for patient in all_patients:
            #Button that displays info for patient, and holds an index which is the patient ID
            self.counter = self.counter + 1
            b = Button(self.frame, text = patient[0] + " - " + patient[1], command = lambda index = patient[0]: self.select_files(index), font = self.text_font)
            b.grid(row = self.counter, column = 0, sticky = "w")
            
            self.btn_list.append(b) #append the button to a button list
            
            #print('{0} : {1}'.format(patient[0],patient[1]))

        self.button_quit = Button(self.frame, text = "Quit", command = self.close_window, font = self.text_font)
        self.button_quit.grid(row = self.counter + 1, column = 0)

        self.frame.grid(row = 0, column = 0, sticky = "nesw")
    
    def submit_method(self):
        print("hello world")
    
    def close_window(self):
        self.master.destroy()
    
    def select_files(self, index):
        #clear window
        self.title.grid_forget()
        self.button_quit.grid_forget()
        for button in self.btn_list:
            button.grid_forget()

        session_filename = filedialog.askopenfilename(filetypes=[("zip", "*.zip")], title = "Select E4 File")
        print("Session filename: " + session_filename)

        timings_filename = filedialog.askopenfilename(filetypes=[("json", "*.json")], title = "Select the Timings File")
        print("Timings filename: " + timings_filename)

        self.title_text.set("New Experiment")
        self.title.grid(row = 0, column = 0)

        Label(self.frame, text = "E4 file: " + session_filename, font = self.text_font).grid(row = 1, column = 0)
        Label(self.frame, text = "Timings file: " + timings_filename, font = self.text_font).grid(row = 2, column = 0)

        self.button_insert_experiment = Button(self.frame, text = "Insert on Database", command = lambda: self.insert_experiment(session_filename, timings_filename, index), font = self.text_font)
        self.button_insert_experiment.grid(row = 3, column = 0)

        self.button_show_experiments = Button(self.frame, text = "Show experiments", command = lambda: self.show_experiments(index), font = self.text_font)
        self.button_show_experiments.grid(row = 4, column = 0)


    def insert_experiment(self, session_name, timings_name, patient_id):
        print(session_name + " " + timings_name + " " + patient_id)

        experiment_number = self.db_obj.get_experiment_number(patient_id) + 1
        
        print("Experiment number is: " + repr(experiment_number))

        self.db_obj.insert_session(experiment_number, session_name, patient_id, timings_name)

        self.button_insert_experiment.grid_forget()

        timings_backup_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Timings"
        copy(timings_name, timings_backup_folder)

        experiment_dest_folder = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\" + patient_id + "\\" + repr(experiment_number)
        
        #create directory and move files
        os.makedirs(experiment_dest_folder)
        move(session_name, experiment_dest_folder)
        move(timings_name, experiment_dest_folder)
        

    def show_experiments(self, index):
        self.db_obj.display_sessions()


#MAIN - DB CREATION
db_obj = DatabaseObject()

db_obj.create_patient_table()
db_obj.create_session_table()


db_obj.display_patients()
db_obj.display_sessions()

#USER INTERFACE
root = Tk()

window = MainWindow(root, db_obj)

root.mainloop()



