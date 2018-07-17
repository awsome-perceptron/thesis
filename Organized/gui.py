from tkinter import *
from tkinter.font import Font
from visualization import DataVisualization
from synchronization_database import DatabaseObject
from session import completeSession
import matplotlib.pyplot as plt
import global_variables as gv

class MainWindow:
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj

        self.frame = Frame(self.master)
        self.bottom_frame = Frame(self.master)

        self.helv36 = Font(family = "Helvetica", size = 36)
        self.hevl18 = Font(family = "Helvetica", size = 18)

        self.button_1 = Button(self.frame, text = "BY PATIENT", fg = "white", bg = "grey", font = self.helv36)
        self.button_1['command'] = lambda: self.open_patients_window()
        self.button_1.pack(fill = "both", expand = "yes")

        self.button_2 = Button(self.bottom_frame, text = "GENERIC", fg = "white", bg = "grey", font = self.helv36)
        self.button_2['command'] = lambda: self.open_generic_window()
        self.button_2.pack(fill = "both", expand = "yes")

        self.frame.pack(fill = "both", expand = "yes")
        self.bottom_frame.pack(fill = "both", expand = "yes")

    def open_patients_window(self):
        self.window_1 = Toplevel(self.master)
        self.patients_window = PatientWindow(self.window_1, self.db_obj)


    def open_generic_window(self):
        self.window_2 = Toplevel(self.master)
        self.periods_window = PeriodWindow(self.window_2, self.db_obj)

class PatientWindow:
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj

        #Fonts
        self.title_font = Font(family = "Helvetica", size = 26)
        self.text_font = Font(family = "Helvetica", size = 16)

        #Lists to handle objects dynamically
        self.counter = 0
        self.open_experiments = 0
        self.btn_list = []
        self.experiment_list = []

        #Layout
        self.frame = Frame(self.master)

        #Declaration of frame, canvas and scrollbar
        self.canvas = Canvas(self.master, borderwidth = 0, background = "#ffffff")
        self.vsbar = Scrollbar(self.master, orient = "vertical", command = self.canvas.yview)
        self.frame = Frame(self.canvas, background = "#ffffff")
        self.canvas.configure(yscrollcommand=self.vsbar.set)

        self.vsbar.pack(side = "right", fill = "y")
        self.canvas.pack(side = "left", fill = "both", expand = True)
        self.canvas.create_window((10,10), window = self.frame, anchor = "nw", tags = "self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        # Declaration of common Labels and Buttons
        self.title_text = StringVar()
        self.first_button_text = StringVar()
        self.second_button_text = StringVar()
        self.third_button_text = StringVar()
        self.fourth_button_text = StringVar()
        self.fifth_button_text = StringVar()

        self.title_label = Label(self.frame, textvar = self.title_text, font = self.title_font)
        self.first_button = Button(self.frame, textvar=self.first_button_text, font=self.text_font)
        self.second_button = Button(self.frame, textvar=self.second_button_text, font=self.text_font)
        self.third_button = Button(self.frame, textvar=self.third_button_text, font=self.text_font)
        self.fourth_button = Button(self.frame, textvar=self.fourth_button_text, font=self.text_font)
        self.fifth_button = Button(self.frame, textvar=self.fifth_button_text, font = self.text_font)

        self.home_button = Button(self.frame, text="Home", command=self.display_patients, font=self.text_font)

        self.display_patients()

    def display_patients(self):
        self.clear_screen()

        self.title_text.set("Select patient")
        self.title_label.pack(side = "top", fill = "both", expand = True)

        all_patients = self.db_obj.query_patients()

        for patient in all_patients:
            self.counter = self.counter + 1
            b = Button(self.frame, text=patient[0] + " - " + patient[1],
                       command=lambda patient_id=patient[0]: self.display_experiments(patient_id), font=self.text_font)
            b.pack(side = "top", fill = "both", expand = True)
            self.btn_list.append(b)

        self.home_button.pack(side = "top", fill = "both", expand = True)
        self.frame.pack( fill = "both", expand = True)

    def display_experiments(self, patient_id):
        self.clear_screen()
        self.title_text.set("Select experiment")
        self.title_label.pack(side = "top", fill = "both", expand = True)

        self.first_button_text.set("Compare experiments")
        self.first_button['command'] = lambda: self.compare_experiments(patient_id)
        self.first_button.pack(side = "top", fill = "both", expand = True)

        all_experiments = self.db_obj.query_patient_experiments(patient_id)

        for experiment in all_experiments:
            self.counter = self.counter + 1
            b = Button(self.frame, text = repr(experiment[0]), command = lambda experiment_number = experiment[0]: self.show_menu(patient_id, experiment_number), font = self.text_font)
            b.pack(side = "top", fill = "both", expand = True)
            self.btn_list.append(b)

        self.home_button.pack(side = "top", fill = "both", expand = True)

    def compare_experiments(self, patient_id):

        pass

    def show_menu(self, patient_id, experiment_number):
        # Create session object
        session = completeSession(patient_id, int(experiment_number))
        view = DataVisualization(session)

        # Layout
        self.clear_screen()
        self.title_text.set("Select an option")
        self.title_label.pack(side = "top", fill = "both", expand = True)

        self.first_button_text.set("Experiment Data")
        self.second_button_text.set("Spectral Density")
        self.third_button_text.set("Autoregressive Coefficients")
        self.fourth_button_text.set("Autoregressive Fit")
        self.fifth_button_text.set("Show")

        self.first_button['command'] = lambda: view.task_data("multiple")
        self.second_button['command'] = lambda: view.power_spectral_density("multiple")
        self.third_button['command'] = lambda: view.ar_coefficients_visualization("multiple")
        self.fourth_button['command'] = lambda: view.ar_model_predictions("multiple")
        self.fifth_button['command'] = lambda: plt.show()

        self.first_button.pack(side = "top", fill = "both", expand = True)
        self.second_button.pack(side="top", fill="both", expand=True)
        self.third_button.pack(side="top", fill="both", expand=True)
        self.fourth_button.pack(side="top", fill="both", expand=True)
        self.fifth_button.pack(side="top", fill="both", expand=True)

        self.home_button.pack(side = "top", fill = "both", expand = True)


    def onFrameConfigure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def clear_screen(self):
        self.title_label.pack_forget()

        self.first_button.pack_forget()
        self.second_button.pack_forget()
        self.third_button.pack_forget()
        self.fourth_button.pack_forget()
        self.fifth_button.pack_forget()

        self.home_button.pack_forget()

        for b in self.btn_list[:]:
            self.counter = self.counter - 1
            b.pack_forget()
            self.btn_list.remove(b)


class PeriodWindow:
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj

if __name__ == "__main__":
    db_obj = DatabaseObject()
    db_obj.create_patient_table()
    db_obj.create_session_table()

    #db_obj.display_patients()
    #db_obj.display_sessions()

    # GUI
    root = Tk()
    window = MainWindow(root, db_obj)

    root.mainloop()