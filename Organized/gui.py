from tkinter import *
from tkinter.font import Font
from visualization import DataVisualization
from synchronization_database import DatabaseObject
from session import CompleteSession
import global_variables as gv
import matplotlib.pyplot as plt
import os


class MainWindow:
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj

        self.frame = Frame(self.master)
        self.bottom_frame = Frame(self.master)

        self.helv36 = Font(family = "Helvetica", size = 36)
        self.hevl18 = Font(family = "Helvetica", size = 18)

        self.button_1 = Button(self.frame, text = "PATIENT", fg = "white", bg = "grey", font = self.helv36)
        self.button_1['command'] = lambda: self.open_patients_window()
        self.button_1.pack(fill = "both", expand = "yes")

        self.button_2 = Button(self.bottom_frame, text = "GROUP", fg = "white", bg = "grey", font = self.helv36)
        self.button_2['command'] = lambda: self.open_group_window()
        self.button_2.pack(fill = "both", expand = "yes")

        self.frame.pack(fill = "both", expand = "yes")
        self.bottom_frame.pack(fill = "both", expand = "yes")

    def open_patients_window(self):
        self.window_1 = Toplevel(self.master)
        self.patients_window = PatientWindow(self.window_1, self.db_obj)

    def open_group_window(self):
        self.window_2 = Toplevel(self.master)
        self.group_window = GroupWindow(self.window_2, self.db_obj)


class PatientWindow:
    def __init__(self, master, db_obj):
        self.master = master
        self.db_obj = db_obj

        #Fonts
        self.title_font = Font(family = "Helvetica", size = 26)
        self.text_font = Font(family = "Helvetica", size = 16)

        #Lists to handle objects dynamically
        self.counter = 0
        self.btn_list = []

        #Call scrollable frame
        self.scrollableFrame = VerticalScrolledFrame(self.master)
        self.scrollableFrame.pack(fill = "both", expand = True)
        self.interior = self.scrollableFrame.interior

        # Title label + Re-usable buttons
        #Button text
        self.title_text = StringVar()
        self.first_button_text = StringVar()
        self.second_button_text = StringVar()
        self.third_button_text = StringVar()
        self.fourth_button_text = StringVar()
        self.fifth_button_text = StringVar()
        #Button widgets
        self.title_label = Label(self.interior, textvar=self.title_text, font=self.title_font)
        self.first_button = Button(self.interior, textvar=self.first_button_text, font=self.text_font)
        self.second_button = Button(self.interior, textvar=self.second_button_text, font=self.text_font)
        self.third_button = Button(self.interior, textvar=self.third_button_text, font=self.text_font)
        self.fourth_button = Button(self.interior, textvar=self.fourth_button_text, font=self.text_font)
        self.fifth_button = Button(self.interior, textvar=self.fifth_button_text, font=self.text_font)

        self.home_button = Button(self.interior, text="Home", command=self.display_patients, font=self.text_font)

        self.display_patients()

    def display_patients(self):
        self.clear_screen()

        self.title_text.set("Select patient")
        self.title_label.pack(fill="both")

        all_patients = self.db_obj.query_patients()

        for patient in all_patients:
            self.counter = self.counter + 1
            b = Button(self.interior, text=patient[0] + " - " + patient[1],
                       command=lambda patient_id=patient[0]: self.display_experiments(patient_id), font=self.text_font)
            b.pack(fill="both")
            self.btn_list.append(b)

        self.home_button.pack(fill="both")

    def display_experiments(self, patient_id):
        self.clear_screen()

        self.title_text.set("Select experiment")
        self.title_label.pack(fill = "both")

        self.first_button_text.set("All experiments")
        self.first_button['command'] = lambda: self.display_visualization_options(patient_id)
        self.first_button.pack(fill = "both")

        #Display list of experiments
        all_experiments = self.db_obj.query_patient_experiments(patient_id)

        for experiment in all_experiments:
            self.counter = self.counter + 1
            b = Button(self.interior, text=repr(experiment[0]), command=lambda experiment_number=experiment[0]: self.display_visualization_options(patient_id, exp_num = experiment_number),
                       font=self.text_font)
            b.pack(fill="both")
            self.btn_list.append(b)

        self.home_button.pack(fill="both")

    def display_visualization_options(self, patient_id, exp_num = None):
        self.clear_screen()

        self.title_text.set("Select an option")
        self.title_label.pack(fill = "both")

        # BUILD SESSION OBJECTS
        sessionList = []

        if exp_num is None:
            for experiment in os.listdir(gv.BASE_FOLDER + patient_id):
                sessionList.append(CompleteSession(patient_id, int(experiment), True))
        else:
            sessionList.append(CompleteSession(patient_id, int(exp_num), True))

        # VISUALIZATION OBJECT
        visualization = DataVisualization(sessionList)

        # TEXT DISPLAY AND METHOD ASSIGNMENT
        text_list = ["Raw Signals", "Raw Detrended Signals", "Raw Magnitude Signals", "Task Actigraphy", "Spectral Density", "AR Coefficients", "Plt Show"]

        function_list = []
        function_list.append(lambda option = "raw_signals": visualization.main(option, "patient"))
        function_list.append(lambda option = "raw_detrended_signals": visualization.main(option, "patient"))
        function_list.append(lambda option="raw_magnitude_signals": visualization.main(option, "patient"))
        function_list.append(lambda option= "task_actigraphy": visualization.main(option, "patient"))
        function_list.append(lambda option= "spectral_density": visualization.main(option, "patient"))
        function_list.append(lambda option="ar_coefficients": visualization.main(option, "patient"))
        function_list.append(lambda: plt.show())


        # Option AR Fitting available only for single experiments
        if exp_num is not None:
            text_list.append("AR Fitting")
            function_list.append(lambda option="ar_fitting": visualization.main_method(option))

        self.dynamic_button_display(text_list, function_list)

        #Set home button
        self.home_button.pack(fill = "both")

    def dynamic_button_display(self, text_list, function_list):
        for i in range(len(text_list)):
            self.counter += 1
            b = Button(self.interior, text = text_list[i], font = self.text_font)
            b['command'] = function_list[i]
            b.pack(fill = "both")
            self.btn_list.append(b)

    def compare_all_experiments(self):
        pass

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


class GroupWindow:
    def __init__(self, master, db_object):
        self.master = master
        self.db_obj = db_object

        self.title_font = Font(family="Helvetica", size=26)
        self.text_font = Font(family="Helvetica", size=16)

        # Lists to handle objects dynamically
        self.counter = 0
        self.btn_list = []

        # Call scrollable frame
        self.scrollableFrame = VerticalScrolledFrame(self.master)
        self.scrollableFrame.pack(fill="both", expand=True)
        self.interior = self.scrollableFrame.interior

        # Title label
        self.title_text = StringVar()
        self.title_label = Label(self.interior, textvar=self.title_text, font=self.title_font)

        # Declaration of common Strings
        self.first_text = StringVar()
        self.second_text = StringVar()
        self.third_text = StringVar()
        self.fourth_text = StringVar()
        self.fifth_text = StringVar()

        # Declaration of common buttons
        self.first_button = Button(self.interior, textvar = self.first_text, font = self.text_font)
        self.second_button = Button(self.interior, textvar = self.second_text, font = self.text_font)
        self.third_button = Button(self.interior, textvar = self.third_text, font = self.text_font)
        self.fourth_button = Button(self.interior, textvar = self.fourth_text, font = self.text_font)
        self.fifth_button = Button(self.interior, textvar = self.fifth_text, font = self.text_font)

        # Home button
        self.home_button = Button(self.interior, text="Home", command=self.display_patients, font=self.text_font)
        self.display_patients()

    def display_patients(self):
        # Important variables
        selected_patients = []
        # Clear screen
        self.clear_screen()

        # Set title
        self.title_text.set("Select all patients to consider")
        self.title_label.pack(fill="both")

        # Display patients
        all_patients = self.db_obj.query_patients()
        for patient in all_patients:
            self.counter = self.counter + 1
            b = Button(self.interior, text=patient[0] + " - " + patient[1], font = self.text_font)
            b['command'] = lambda patient_id = patient[0]: selected_patients.append(patient_id)
            b.pack(fill="both")
            self.btn_list.append(b)

        # Submit button
        self.first_text.set("Submit")
        self.first_button['command'] = lambda: self.display_options(selected_patients)
        self.first_button.pack(fill="both")

        self.home_button.pack(fill="both")

    def display_options(self, selected_patients):
        # Clear Screen
        self.clear_screen()

        # Title set
        self.title_text.set("Select an option")
        self.title_label.pack(fill = "both")

        # Creation of session list
        sessions = []

        for patient in selected_patients:
            for experiment in os.listdir(gv.BASE_FOLDER + patient):
                session_obj = CompleteSession(patient, int(experiment), True)
                sessions.append(session_obj)

        visualization = DataVisualization(sessions)

        # Display options
        text_list = ["Raw Signals", "Raw Detrended Signals", "Raw Magnitude Signals", "Task Actigraphy", "Spectral Density", "AR Coefficients", "Plt Show"]
        function_list = []

        function_list = []
        function_list.append(lambda option="raw_signals": visualization.main(option, "group"))
        function_list.append(lambda option="raw_detrended_signals": visualization.main(option, "group"))
        function_list.append(lambda option="raw_magnitude_signals": visualization.main(option, "group"))
        function_list.append(lambda option="task_actigraphy": visualization.main(option, "group"))
        function_list.append(lambda option="spectral_density": visualization.main(option, "group"))
        function_list.append(lambda option="ar_coefficients": visualization.main(option, "group"))
        function_list.append(lambda: plt.show())

        self.dynamic_button_display(text_list, function_list)

    def dynamic_button_display(self, text_list, function_list):
        for i in range(len(text_list)):
            self.counter += 1
            b = Button(self.interior, text = text_list[i], font = self.text_font)
            b['command'] = function_list[i]
            b.pack(fill = "both")
            self.btn_list.append(b)

    def clear_screen(self):
        self.title_label.pack_forget()
        self.first_button.pack_forget()
        self.second_button.pack_forget()
        self.third_button.pack_forget()
        self.fourth_button.pack_forget()
        self.fifth_button.pack_forget()

        for b in self.btn_list[:]:
            self.counter = self.counter - 1
            b.pack_forget()
            self.btn_list.remove(b)

        self.home_button.pack_forget()


class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """

    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient="vertical")
        vscrollbar.pack(fill="y", side="right", expand=False)
        canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=vscrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=self.interior,
                                           anchor="nw")

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if self.interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=self.interior.winfo_reqwidth())

        self.interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if self.interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())

        canvas.bind('<Configure>', _configure_canvas)


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