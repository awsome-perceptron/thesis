#!/usr/bin/python

from tkinter import Tk, Label, Button, StringVar, Text, INSERT, Canvas, Entry
from datetime import datetime
import time
import json

class myFirstGUI:
    def __init__(self, master):
        self.master = master
        self.my_blue_button = "#006a9b"
        self.background = "#4E4E50"
        master.title = ("Aquisição de dados")
        self.my_blue = "#13E7EB"

        #flags for HRV bar movement
        self.active = False
        self.increase = True

        self.background_label = Label(master, background = self.background)
        self.background_label.place(x = 0, y =0, relwidth = 1, relheight = 1)

        self.title_string = StringVar()
        self.title_string.set("")

        self.title_widget = Label(self.background_label, textvariable = self.title_string, font = ("Helvetica", 30), foreground = "#ffffff", background = self.background)
        self.instruction_string = StringVar()
        self.instruction_string.set("")
        self.instruction_label = Label(self.background_label, textvariable = self.instruction_string, font = ("Helvetica", 18), foreground = "#ffffff", background = self.background)
        
        
        self.button_string = StringVar()
        self.button_string.set("Comecar")
        self.next_button = Button(self.background_label, textvariable = self.button_string, font = ("Helvetica", 14), foreground = "#ffffff", background = self.my_blue_button)
        self.next_button.config(width = len("Clique para começar!") + 2)
        self.next_button['command'] = lambda: self.start_callback()

        self.place_common_widgets()

    def start_callback(self):
        print("hello world")

root = Tk()
my_gui = myFirstGUI(root)
root.mainloop()
