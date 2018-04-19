#!/usr/bin/python

from tkinter import Tk, Label, Button, StringVar, Text, INSERT, Canvas, Entry
from datetime import datetime
import time
import json
import random

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
        self.title_string.set("Bem-vindo!")

        self.title_widget = Label(self.background_label, textvariable = self.title_string, font = ("Helvetica", 30), foreground = "#ffffff", background = self.background)
        self.instruction_string = StringVar()
        self.instruction_string.set("Iremos começar em breve. Por favor aguarde.")
        self.instruction_label = Label(self.background_label, textvariable = self.instruction_string, font = ("Helvetica", 18), foreground = "#ffffff", background = self.background)
        
        
        self.button_string = StringVar()
        self.button_string.set("Clique para começar!")
        self.next_button = Button(self.background_label, textvariable = self.button_string, font = ("Helvetica", 14), foreground = "#ffffff", background = self.my_blue_button)
        self.next_button.config(width = len("Clique para começar!") + 2)
        self.next_button['command'] = lambda: self.start_callback()

        self.place_common_widgets()

    def start_callback(self):
        #create timestamps objects, to store all the relevant times
        self.experimentTimestamps = experimentTimeObject(time.perf_counter(), datetime.now(), time.time())
        
        #change layout for heart rate variability instructions
        self.forget_common_widgets()

        #prepare new screen
        self.title_string.set("Relaxamento \n")
        self.instruction_string.set("Na primeira parte apenas deverá relaxar e respirar normalmente durante 4 minutos. \n\n  Na segunda parte deverá tentar sincronizar o padrão respiratório com uma animação, durante 2 minutos. \n\n Mantenha-se relaxado.\n")
        self.button_string.set("Entendido")
        self.next_button['command'] = lambda: self.start_hrv_test()

        self.place_common_widgets()

    def start_hrv_test(self):
        self.experimentTimestamps.add_entry("breathing_begin", time.perf_counter())

        #call function that skips one minute, to measure stuff at baseline

        self.my_yellow = "#F5F50F"
        #update HRV bar movement flag
        self.active = True
        self.baseline = True

        self.breathing_instruction = StringVar()
        self.breathing_instruction.set("INSPIRE")

        #Add key to skip HRV part of the test. If the user presses the "s" key, it will go to the next part of the test
        self.master.bind("<s>", self.start_pvt)

        #variables that define the interval between consecutive breathings and experiment duration
        self.total_duration = 6 * 60 #total time of 6 minutes, expressed in seconds
        self.breathing_interval = 5 #means that patient should inspire for 5 seconds, and expire for 5 seconds. 10 seconds total breathing intervals

        self.forget_common_widgets()

        #add title again
        self.background_label.place(x = 0, y =0, relwidth = 1, relheight = 1)
        self.title_widget.place(relx = 0.5, rely = 0.2, anchor = "center")

        #draw background rectangle
        self.static_width = 800
        self.rectangle = Canvas(self.background_label, bg = self.background, width = self.static_width, height = 150)
        #self.rectangle.place(relx = 0.5, rely = 0.4, anchor = "center")
        
        #draw first moving rectangle
        self.variable_width = 0
        self.rectangle_variable = Canvas(self.rectangle, bg = self.my_yellow, width = self.variable_width, height = 150)
        #self.rectangle_variable.place(relx = 0, rely = 0)

        #draw first breathing instruction 
        self.instruction_widget = Label(self.background_label, textvariable = self.breathing_instruction, font = ("Helvetica", 65), background = self.background, foreground = self.my_yellow)
        #self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
        
        #measure initial time
        self.initial_time = time.time()

        #declare widgets for baseline layout
        self.relaxation_widget = Label(self.background_label, text = "Respire normalmente durante 4 minutos.", font = ("Helvetica", 22), background = self.background, foreground = "#ffffff")
        self.relaxation_widget2 = Label(self.background_label, text = "Permaneça relaxado." , font = ("Helvetica", 22), background = self.background, foreground = "#ffffff")
        self.remaining_time = StringVar()
        self.countdown_clock = Label(self.background_label, textvariable = self.remaining_time, font = ("Helvetica", 35), background = self.background, foreground = "#49a834")

        #call meque no botãthod that will start iterative updates
        self.master.bind("<d>", self.delete_this) #just for debug
        
        self.remaining_time.set("04:00")
        self.old_seconds = 0
        self.relaxation_widget.place(relx = 0.5, rely = 0.40, anchor = "center")
        self.relaxation_widget2.place(relx = 0.5, rely = 0.65, anchor = "center")
        self.countdown_clock.place(relx = 0.50, rely = 0.80, anchor = "center")

        self.move_rectangle()


    def hrv_clear_rectangles(self):
        #this function was developed later, that's why it's not used everywhere
        self.rectangle.place_forget()
        self.rectangle_variable.place_forget()
        self.instruction_widget.place_forget()
        self.title_widget.place_forget()

    def hrv_place_rectangles(self):
        self.background_label.place(x = 0, y =0, relwidth = 1, relheight = 1)
        self.rectangle.place(relx = 0.5, rely = 0.4, anchor = "center")
        
        self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
        self.title_widget.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.rectangle_variable.place(relx = 0, rely = 0)

    def rectangle_update(self):
        actual_time = time.time()

        #Decision if rectangle should grow or get smaller depends on 3 factors: time is an independent one and should be verified here.
        #The others factors are width below 0 or above 800. Any of these events will shift the direction of growth. 
        if actual_time - self.iteration_start_time > 5:
            self.iteration_start_time = time.time()
            if self.increase:
                self.increase = False
                #update instruction widget
                self.title_widget.place_forget()
                self.instruction_widget.place_forget()
                self.breathing_instruction.set("EXPIRE")
                self.instruction_widget.config(foreground = self.my_blue)
                self.rectangle_variable.config(bg = self.my_blue)
                self.title_widget.place(relx = 0.5, rely = 0.20, anchor = "center")
                
            else:
                self.increase = True
                #update instruction widget
                self.title_widget.place_forget()
                self.instruction_widget.place_forget()
                self.breathing_instruction.set("INSPIRE")
                self.instruction_widget.config(foreground = self.my_yellow)                
                self.rectangle_variable.config(bg = self.my_yellow)
                self.title_widget.place(relx = 0.5, rely = 0.20, anchor = "center")

        #Either way, increase or decrease is proportional to time left for 5 seconds
        if(self.increase):
            #width increase
            self.variable_width = (self.static_width / self.breathing_interval) * (actual_time - self.iteration_start_time)
            #Shift growth direction
            if self.variable_width > 800: 
                self.variable_width = 800
                self.increase = False
                self.iteration_start_time = time.time()
                #update instruction widget
                self.instruction_widget.place_forget()
                self.breathing_instruction.set("INSPIRE")
                self.instruction_widget.config(foreground = self.my_yellow)
                self.rectangle_variable.config(bg = self.my_yellow)
        else:                                 
            #width decrease
            self.variable_width = self.static_width - ( (self.static_width/self.breathing_interval) * (actual_time - self.iteration_start_time) )
            #shift growth direction
            if self.variable_width < 0:
                self.variable_width = 0
                self.increase = True
                self.iteration_start_time = time.time()
                #update instruction widget
                self.instruction_widget.place_forget()
                self.breathing_instruction.set("EXPIRE")
                self.instruction_widget.config(foreground = self.my_blue)
                self.rectangle_variable.config(bg = self.my_blue)

        
        #clear layout
        
        # self.title_widget.place_forget()
        
        # self.instruction_widget.place_forget()
        # self.rectangle.place_forget()
        # self.background_label.place_forget()
        
        #call functions to draw the new rectangle
        self.rectangle_variable.place_forget()
        self.rectangle_variable.config(width = self.variable_width)
        self.rectangle_variable.place(relx = 0, rely = 0)
        self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
    	

        # self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
        # self.rectangle.place(relx = 0.5, rely = 0.4, anchor = "center")
        # self.title_widget.place(relx = 0.5, rely = 0.20, anchor = "center")
        # self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
        # self.rectangle_variable.place(relx = 0, rely = 0)

        #after the update, check if the total experiment time was acchieved
        if actual_time - self.initial_time > self.total_duration:
            #move on to next test. Call method that starts PVT
            self.active = False
            self.start_pvt()

    def layout_baseline(self):
        now = time.time()
        seconds = int(4*60 - (now - self.initial_time))

        if seconds != self.old_seconds:        
            #clear layout
            self.background_label.place_forget()
            self.title_widget.place_forget()
            self.relaxation_widget.place_forget()
            self.relaxation_widget2.place_forget()
            self.countdown_clock.place_forget()

            self.remaining_time.set(repr(int(seconds/60)) + ":" + repr(seconds % 60))

            #set layout
            self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)      
            self.title_widget.place(relx = 0.5, rely = 0.20, anchor = "center")
            self.relaxation_widget.place(relx = 0.5, rely = 0.40, anchor = "center")
            self.relaxation_widget2.place(relx = 0.5, rely = 0.65, anchor = "center")
            self.countdown_clock.place(relx = 0.5, rely = 0.80, anchor = "center")

        self.old_seconds = seconds

    def delete_this(self, event = None):
        #this is just to debug, to skip the base line faster. after pressing the button <d> the baseline ends in 20 seconds, and then deep breathing starts
        self.initial_time = time.time() - 55*4

    def move_rectangle(self):
        now = time.time()
        if self.active:
            if (now - self.initial_time) < 60 * 4:
                #the first 4 minute is just to measure baseline and relax
                if self.baseline == True:
                    self.layout_baseline()
                    self.call_identifier = self.master.after(100, self.move_rectangle)
                
            else:
                if self.baseline == True:
                    self.baseline = False
                    self.background_label.place_forget()
                    self.title_widget.place_forget()
                    self.relaxation_widget.place_forget()
                    self.relaxation_widget2.place_forget()
                    self.countdown_clock.place_forget()

                    self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)      
                    self.title_widget.place(relx = 0.5, rely = 0.20, anchor = "center")
                    self.rectangle.place(relx = 0.5, rely = 0.4, anchor = "center")
                    self.rectangle_variable.place(relx = 0, rely = 0)
                    self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
                    self.iteration_start_time = time.time()

                self.rectangle_update()
                self.call_identifier = self.master.after(20, self.move_rectangle)

    def start_pvt(self, event = None):
        self.experimentTimestamps.add_entry("breathing_end", time.perf_counter())
        #make sure that hrv part has finished
        self.active = False

        #unbind previous binds
        self.master.unbind("<d>")
        self.master.unbind("<s>")

        #clear screen
        self.rectangle.place_forget()
        self.rectangle_variable.place_forget()
        self.relaxation_widget.place_forget()
        self.relaxation_widget2.place_forget()
        self.instruction_widget.place_forget()
        self.countdown_clock.place_forget()
        self.forget_common_widgets()

        #set new layout
        self.title_string.set("Reação")
        self.instruction_string.set("No ecrã seguinte irá observar um rectângulo de cor verde, que mudará de cor para vermelho. \n\n Quando isto acontecer, clique no botão esquerdo do rato assim que conseguir. \n\n Isto irá suceder 5 vezes. Evite clicar antes do tempo. \n")
        self.next_button['command'] = lambda: self.pvt_test()
        self.place_common_widgets()

    def pvt_test(self):
        self.experimentTimestamps.add_entry("pvt_begin", time.perf_counter())
        self.pvt_tries = 5
        self.pvt_counter = 0
        self.pvt_errors = 0
        self.pvt_active = False
        self.pvt_green = "#20E820"
        self.pvt_red =  "#ED1F1F"

        #generate random switch times
        self.switch_time = self.pvt_randomize_switch_time()
        print(self.switch_time)

        #associate <s> key to skip pvt test
        self.master.bind("<s>", self.signature_instruction_layout)

        #bind mouse1 to click
        self.master.bind("<Button-1>", self.pvt_click_detected)

        #configure screen layout
        self.forget_common_widgets()
        self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)

        self.pvt_box = Canvas(self.background_label, bg = self.pvt_green, width = 800, height = 300)
        self.pvt_box.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.breathing_instruction.set("PREPARE-SE")
        self.instruction_widget.config(foreground = self.my_yellow, font = ("Helvetica", 50))
        self.instruction_widget.place(relx = 0.5, rely = 0.70, anchor = "center")
        self.title_widget.place(relx = 0.5, rely = 0.10, anchor = "center")

        self.pvt_iteration_start_time = time.perf_counter()

        #get things rolling
        self.pvt_iteration()

    def pvt_iteration(self):
        if self.pvt_counter < 5:
            self.pvt_update()
        else:
            self.signature_instruction_layout()

    def pvt_update(self):
        
        time_dif = time.perf_counter() - self.pvt_iteration_start_time 
        
        if time_dif >= self.switch_time[str(self.pvt_counter)]:
            self.title_widget.place_forget()
            self.title_widget.place(relx = 0.5, rely = 0.1, anchor = "center")
            self.instruction_widget.place_forget()
            self.instruction_widget.place(relx = 0.5, rely = 0.70, anchor = "center")
            self.pvt_active = True

            self.pvt_box.place_forget()
            self.pvt_box.config(bg = self.pvt_red)
            print("Turned red now")
            self.pvt_box.place(relx = 0.5, rely = 0.4, anchor = "center")
            self.reaction_ini_time = time.perf_counter()
        else:
            if self.pvt_counter < 5:
                self.call_identifier = self.master.after(10, self.pvt_update)
        
    def pvt_click_detected(self, event = None):
        self.reaction_end_time = time.perf_counter()
        
        if self.pvt_active == False:
            #user clicked on mouse1 before the correct time
            #maybe display saying something like: chillout or a buzzing noise
            self.reaction_end_time = None
            self.pvt_errors = self.pvt_errors + 1
            #self.experimentTimestamps.add_entry("PVT_MISTAKE", "MISTAKE") do this in the end
            self.pvt_iteration_start_time = time.perf_counter()
        else:
            self.reaction_time = self.reaction_end_time - self.reaction_ini_time
            
            print('Reaction time number ', self.pvt_counter)
            self.experimentTimestamps.add_entry("pvt_" + str(self.pvt_counter), str(self.reaction_time))
            self.experimentTimestamps.add_entry("pvt_begin_" + str(self.pvt_counter), self.reaction_ini_time)
            self.experimentTimestamps.add_entry("pvt_end_" + str(self.pvt_counter), self.reaction_end_time)

            #restore control variables and layout
            self.title_widget.place_forget()
            self.title_widget.place(relx = 0.5, rely = 0.1, anchor = "center")
            self.pvt_box.place_forget()
            self.pvt_box.config(bg = self.pvt_green)
            self.pvt_box.place(relx = 0.5, rely = 0.4, anchor = "center")
            self.instruction_widget.place_forget()
            self.instruction_widget.place(relx = 0.5, rely = 0.70, anchor = "center")
            self.pvt_active = False
            self.pvt_counter = self.pvt_counter + 1

            self.pvt_iteration_start_time = time.perf_counter()
            self.pvt_iteration()

    def pvt_randomize_switch_time(self):
        times = [3, 4, 5, 7, 10]
        dic = {}

        for i in range(len(times)):
            selected = random.choice(times)
            times.remove(selected)
            dic[repr(i)] = selected

        return dic

    def signature_instruction_layout(self, event = None):
        self.experimentTimestamps.add_entry("pvt_end", time.perf_counter())
        self.experimentTimestamps.add_entry("pvt_errors", self.pvt_errors)

        #control variables for this test
        self.number_signatures = 5
        self.signature_counter = 0

        #disable old flags
        self.pvt_active = False
        self.pvt_counter = 10 #just to be higher than 5, it's not necessary probably 

        #unbind
        self.master.unbind("<Button-1>")
        self.master.unbind("<s>")

        #clear window
        self.pvt_box.place_forget()
        self.instruction_widget.place_forget()
        self.forget_common_widgets()
        
        #set new layout
        self.title_string.set("Escrita do nome")
        self.instruction_string.set("Pretende-se que escreva o seu nome completo " + repr(self.number_signatures) + " vezes. \n\n Para tal, irá receber uma folha em branco com diversas caixinhas. \n\n Apenas deve começar a escrever o nome quando receber indicação para tal. \n\n Quando terminar a escrita do nome, deverá avisar que terminou. \n")
        self.next_button['command'] = lambda: self.signature_test()
        self.place_common_widgets()

    def signature_test(self):
        self.experimentTimestamps.add_entry("signature_begin", time.perf_counter())

        #change layout
        self.forget_common_widgets()

        self.instruction_string.set("Clique no botão abaixo para começar a escrita do nome. \n")
        self.breathing_instruction.set("NÚMERO DE ASSINATURAS OBTIDAS: " + repr(self.signature_counter))
        self.button_string.set("Começar")

        self.instruction_widget.config(fg = self.pvt_green, font = ("Helvetica", 30))
        self.next_button['command'] = lambda: self.signature_begin()

        self.place_common_widgets()
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
             
    def signature_begin(self):
        self.experimentTimestamps.add_entry("signature_begin_" + str(self.signature_counter), time.perf_counter())
        
        self.forget_common_widgets()
        self.instruction_string.set("Clique no botão quando a escrita do nome tiver terminado. \n")
        self.button_string.set("Terminar")
        self.next_button['command'] = lambda: self.signature_finish()
        self.place_common_widgets()
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
        #self.breathing_instruction.set("NÚMERO DE ASSINATURAS OBTIDAS: " + repr(self.signature_counter))
        
    def signature_finish(self):
        self.experimentTimestamps.add_entry("signature_end_" + str(self.signature_counter), time.perf_counter())
        self.signature_counter = self.signature_counter + 1
        
        #change layout
        self.forget_common_widgets()

        self.instruction_string.set("Clique no botão abaixo para começar a escrita do nome. \n")
        self.breathing_instruction.set("NÚMERO DE ASSINATURAS OBTIDAS: " + repr(self.signature_counter))
        self.button_string.set("Começar")

        self.next_button['command'] = lambda: self.signature_begin()

        self.place_common_widgets()
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
        
        if self.signature_counter == self.number_signatures:
            #next experiment
            #call function for next experiment
            self.transcription_layout()

    def transcription_layout(self):
        self.experimentTimestamps.add_entry("signature_end", time.perf_counter())

        #clear screen
        self.instruction_widget.place_forget()
        self.forget_common_widgets()

        self.title_string.set("Transcrição de texto")
        self.instruction_string.set("No ecrã seguinte irá aparecer um pequeno texto. \n\n Deverá copiar esse texto para uma folha branca que lhe será fornecida.\n\n Tente completar a tarefa o mais rápido que consiga, sem cometer erros. \n\n")
        self.button_string.set("Começar")
        self.next_button['command'] = lambda: self.start_transcription()

        self.place_common_widgets()

    def start_transcription(self):
        self.experimentTimestamps.add_entry("transcription_begin", time.perf_counter())

        #clear screen
        self.instruction_widget.place_forget()
        self.forget_common_widgets()

        self.title_string.set("Transcrição de texto")

        self.transcription_text = "A tendência que leva os portugueses a terem cada vez mais filhos fora do casamento não é recente e foi nesta terça-feira quantificada pelo Eurostat: Portugal é um dos oito estados-membros da União Europeia onde mais de metade dos bebés nasceram fora do casamento: 52,8%, em 2016. Segundo o gabinete de estatísticas da União Europeia (UE), naquele ano a França encabeçou a lista ao somar 59,7% de crianças nascidas fora do casamento. \n\n"
        self.transcription_widget = Label(self.background_label, text = self.transcription_text, font = ("Helvetica", 18), foreground = "#ffffff", background = self.background, wraplength=850)
        self.instruction_string.set("")

        self.button_string.set("Terminar")
        self.next_button['command'] = lambda: self.drawing_layout()

        self.place_common_widgets()
        self.transcription_widget.place(relx = 0.2, rely = 0.5, anchor = "w")
        self.next_button.place(relx = 0.5, rely = 0.85, anchor = "center")
    
    def drawing_layout(self):
        self.experimentTimestamps.add_entry("transcription_end", time.perf_counter())

        #CONTROL VARIABLES
        self.number_drawings = 3
        self.actual_drawings = 0

        #clear screen
        self.instruction_widget.place_forget()
        self.transcription_widget.place_forget()
        self.forget_common_widgets()

        self.title_string.set("Desenhar")
        self.instruction_string.set("No ecrã seguinte será apresentada uma hora, em formato digital.\n Numa folha em branco, deverá desenhar um relógio e os ponteiros que representam essa mesma hora.\n\n Para além dos ponteiros, deverá desenhar também os números do relógio. \n Ao todo, deverá realizar esta tarefa com 3 horas diferentes. Tente terminar o mais rápido que conseguir.\n")
        self.button_string.set("Começar")
        self.next_button['command'] = lambda: self.start_drawing()

    
        self.random_time = StringVar()
        self.time_widget = Label(self.background_label, textvariable = self.random_time, font = ("Helvetica", 40), background = self.background, foreground = self.my_yellow)

        self.place_common_widgets()
    
    def start_drawing(self):
        self.experimentTimestamps.add_entry("drawing_begin_" + repr(self.actual_drawings), time.perf_counter())

        #clear screen
        self.instruction_widget.place_forget()
        self.time_widget.place_forget()
        self.forget_common_widgets()

        self.title_string.set("Desenhar")
        self.instruction_string.set("Clique no botão abaixo quando terminar de desenhar. \n")
        #place time to draw
        self.random_time.set(self.generateRandomTime())

        self.button_string.set("Terminar")
        self.next_button['command'] = lambda: self.drawing_increment()

        self.place_common_widgets()
        self.time_widget.place(relx = 0.5, rely = 0.55, anchor = "center")

    def drawing_increment(self):
        self.experimentTimestamps.add_entry("drawing_end_" + repr(self.actual_drawings), time.perf_counter())

        self.actual_drawings = self.actual_drawings + 1

        if self.actual_drawings == self.number_drawings:
            self.tma_layout()
        else:
            self.start_drawing()

    def generateRandomTime(self):
        hours_list = [1,2,3,4,5,6,7,8,9,10,11,12]
        minutes_list = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]

        hour = random.choice(hours_list)
        minutes = random.choice(minutes_list)

        #do something
        return repr(hour) + " horas e " + repr(minutes) + " minutos."

    def tma_layout(self):
        self.experimentTimestamps.add_entry("drawing_end", time.perf_counter())

        #clear screen
        self.instruction_widget.place_forget()
        self.time_widget.place_forget()
        self.forget_common_widgets()

        self.title_string.set("Trail Making Test - Parte A")
        self.instruction_string.set("Irá receber uma folha com diversas bolas numeradas, tal como nesta amostra. \n\n Pretende-se que una as bolas de forma sequencial, sem levantar a caneta. \n\n Resolva o exercício o mais rápido que conseguir, sem cometer erros. \n")
        self.button_string.set("Começar")
        self.next_button['command'] = lambda: self.start_tma()

        self.place_common_widgets()

    def start_tma(self):
        self.experimentTimestamps.add_entry("tma_begin", time.perf_counter())

        self.forget_common_widgets()

        self.instruction_string.set("Quando o teste terminar, clique no botão abaixo.")
        self.button_string.set("Terminado")
        self.next_button['command'] = lambda: self.tmb_layout()

        self.place_common_widgets()

        self.ini_time_tma = datetime.now()
    
    def tmb_layout(self):
        self.experimentTimestamps.add_entry("tma_end", time.perf_counter())

        self.end_time_tma = datetime.now()
        dif = self.end_time_tma - self.ini_time_tma
        print("TRAIL MAKING A: Demorou " + repr(dif.seconds) + " a completar a primeira parte do teste.")

        self.forget_common_widgets()
        self.title_string.set("Trail Making Test - Parte B")
        self.instruction_string.set("Irá receber uma folha com diversas bolas numeradas, tal como nesta amostra. \n\n Pretende-se que una as bolas de forma sequencial, sem levantar a caneta. \n\n Resolva o exercício o mais rápido que conseguir, sem cometer erros. \n")
        self.button_string.set("Começar")
        self.next_button['command'] = lambda: self.start_tmb()

        self.place_common_widgets()

    def start_tmb(self):
        self.experimentTimestamps.add_entry("tmb_begin", time.perf_counter())

        self.forget_common_widgets()
        self.instruction_string.set("Quando terminar o teste, clique no botão abaixo.")
        self.button_string.set("Terminado")
        self.next_button['command'] = lambda: self.fingertapping_layout()
        
        self.place_common_widgets()

        self.ini_time_tmb = datetime.now()

    def fingertapping_layout(self):
        self.experimentTimestamps.add_entry("tmb_end", time.perf_counter())

        self.tap_duration = 60 #seconds
        self.tap_counter = 0

        self.forget_common_widgets()
        self.title_string.set("Cliques")
        self.instruction_string.set("Durante um minuto, clique no botão esquerdo do rato o maior número de vezes que conseguir.\n")
        self.button_string.set("Começar")
        self.next_button['command'] = lambda: self.fingertapping_start()

        self.place_common_widgets()

    def fingertapping_start(self):
        self.experimentTimestamps.add_entry("tapping_begin", time.perf_counter())
        self.master.bind("<Button-1>", self.tap_detected)
        self.master.bind("<s>", self.physical_layout)

        self.forget_common_widgets()
        self.instruction_string.set("Continue a clicar!")
        self.breathing_instruction.set("Número de cliques: " + repr(self.tap_counter))
        
        self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
        self.title_widget.place(relx = 0.5, rely = 0.15, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.tapping_ini_time = time.perf_counter()

    def tap_detected(self, event = None):
        self.experimentTimestamps.add_entry("tapping_" + str(self.tap_counter), time.perf_counter())

        self.tap_counter = self.tap_counter + 1
        
        self.forget_common_widgets()
        self.instruction_widget.place_forget()
        self.breathing_instruction.set("Número de cliques: " + repr(self.tap_counter))
        
        self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
        self.title_widget.place(relx = 0.5, rely = 0.15, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")

        if time.perf_counter() - self.tapping_ini_time > self.tap_duration:
            self.physical_layout()

    def physical_layout(self, event = None):
        self.experimentTimestamps.add_entry("tapping_end", time.perf_counter())
        self.experimentTimestamps.add_entry("tapping_total", self.tap_counter)
        
        #unbind
        self.master.unbind("<Button-1>")
        self.master.unbind("<s>")

        #set new layout
        self.instruction_widget.place_forget()
        self.forget_common_widgets()

        self.title_string.set("Circuito")
        self.instruction_string.set("Coloque a pulseira no braço não dominante. \n\n Siga as instruções que lhe forem indicadas. \n\n Caminhe normalmente. \n")
        self.button_string.set("Começar")
        self.next_button['command'] = lambda: self.start_physical()
        
        self.place_common_widgets()

    def start_physical(self):
        self.experimentTimestamps.add_entry("physical_begin", time.perf_counter())
        self.ini_time_physical = datetime.now()

        self.physical_tests_counter = 0
        self.number_physical_tests = 6

        self.forget_common_widgets()

        self.breathing_instruction.set("NÚMERO DE VOLTAS TERMINADAS: " + repr(self.physical_tests_counter))
        self.instruction_string.set("Clique no botão abaixo sempre que uma volta for terminada")

        self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
        self.title_widget.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.3, anchor = "center")
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.7, anchor = "center")

       
        self.button_string.set("Incrementar")
        self.next_button['command'] = lambda: self.physical_increment()

    def physical_increment(self, event = None):
        self.experimentTimestamps.add_entry("physical_" + str(self.physical_tests_counter), time.perf_counter())
        self.physical_tests_counter = self.physical_tests_counter + 1

        self.forget_common_widgets()

        self.breathing_instruction.set("NÚMERO DE VOLTAS TERMINADAS: " + repr(self.physical_tests_counter))
        self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
        self.title_widget.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.3, anchor = "center")
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.7, anchor = "center")

        if self.physical_tests_counter == self.number_physical_tests:
            self.thankyou_layout()

    def thankyou_layout(self):
        self.experimentTimestamps.add_entry("physical_end", time.perf_counter())
        
        self.instruction_widget.place_forget()
        self.forget_common_widgets()

        self.title_string.set("Terminado")
        self.instruction_string.set("Muito obrigado pelo seu contributo!")
        self.button_string.set("Exportar dados")
        self.next_button['command'] = lambda: self.export_intervals()
        
        self.place_common_widgets()

    def export_intervals(self):
        #prompt for patient name in 
        self.patient_name = input("Escreva o nome do paciente: ")
        filename = self.patient_name + "_" + str(self.experimentTimestamps.epoch)

        filename = filename.replace(" ", "_")
        filename = filename.replace(":", "-")
        filename = filename.replace(".", "-")
    

        print("Name of file %s", filename)
        
        with open(filename + '.json', "w") as fp:
            json.dump(self.experimentTimestamps.stamp_dict, fp)

    def place_common_widgets(self):
        self.background_label.place(x = 0, y = 0, relwidth = 1, relheight = 1)
        self.title_widget.place(relx = 0.5, rely = 0.15, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.65, anchor ="center")

    def forget_common_widgets(self):
        self.background_label.place_forget()
        self.title_widget.place_forget()
        self.instruction_label.place_forget()
        self.next_button.place_forget()

class experimentTimeObject:
    #This class contains a dictionary (stamp_dict) to keep track of the time intervals corresponding to the different tests
    
    def __init__(self, time, date, epoch):
        #store initial stamp: number of seconds since epoch, that should be used to sync with the wristband timestamp
        self.initial_stamp = time
        self.start_date = date
        self.epoch = epoch
        #note: perf_counter is not to measure absolute time. only differences between them have value
        
        self.stamp_dict = {'experiment_start': time, 'timestamp_start': str(date), 'epoch_start': epoch}
        
        print("experiment_start: ", self.stamp_dict['experiment_start'])
        self.debug = True      

    def add_entry(self, key, time):
        #keys will have the format "t_i", in which "i" is an index. the total experiment has 23 different times.
        self.stamp_dict[key] = time
        if self.debug:
            print(key, self.stamp_dict[key])

    def calculate_time_intervals(self):
        #create new dictionary, that contains both the begin and end time for the different experiment parts
        self.intervals_dict = {}
        #according to the design experiment, e.g the signature info will be between two intervals. basically this intervals will be used to separate the data in several segments.
    
    def print_dictionary(dict):
        for keys,values in dict.items():
            print("['",keys,"'] = ", values, " \n")

    def set_patient_name(self, name):
        self.name = name


root = Tk()
my_gui = myFirstGUI(root)
root.mainloop()
