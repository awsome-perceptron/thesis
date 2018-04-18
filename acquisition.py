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

        #flag for HRV bar movement
        self.active = False
        self.increase = True

        self.background_label = Label(master, background = self.background)
        self.background_label.place(x = 0, y =0, relwidth = 1, relheight = 1)

        self.title_string = StringVar()
        self.title_string.set("Bem-vindo!")
        self.title_w = Label(self.background_label, textvariable = self.title_string, font = ("Helvetica", 30), foreground = "#ffffff", background = self.background)
        self.title_w.place(relx = 0.5, rely = 0.3, anchor = "center")

        self.instruction_string = StringVar()
        self.instruction_string.set("O teste irá começar em breve. Por favor aguarde")
        self.instruction_label = Label(self.background_label, textvariable = self.instruction_string, font = ("Helvetica", 18), foreground = "#ffffff", background = self.background)
        self.instruction_label.place(relx = 0.5, rely = 0.4, anchor = "center")
        
        self.button_string = StringVar()
        self.button_string.set("Clique para começar!")
        self.next_button = Button(self.background_label, textvariable = self.button_string, font = ("Helvetica", 14), foreground = "#ffffff", background = self.my_blue_button)
        self.next_button.config(width = len("Clique para começar!") + 2)
        self.next_button['command'] = lambda: self.start_callback()
        self.next_button.place(relx = 0.5, rely = 0.5, anchor ="center")

    def start_callback(self):
        #create timestamps objects, to store all the relevant times
        self.experimentTimestamps = experimentTimeObject(time.perf_counter(), datetime.now(), time.time())
        #change layout for heart rate variability instructions
        self.title_w.place_forget()
        self.title_string.set("Variabilidade da Frequência Cardíaca\n")
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")


        self.instruction_string.set("No ecrã seguinte será apresentada uma animação. Tente que o seu padrão respiratório siga a animação. \n\n Tente manter-se relaxado.\n")
        
        self.button_string.set("Entendi")
        self.next_button['command'] = lambda: self.start_hrv_test()
        self.next_button.place(relx = 0.5, rely = 0.6)

    def start_hrv_test(self):
        self.experimentTimestamps.add_entry("t2", time.perf_counter())

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
        self.total_duration = 4 * 60 #total time of 5 minutes, expressed in seconds
        self.breathing_interval = 5 #means that patient should inspire for 5 seconds, and expire for 5 seconds. 10 seconds total breathing intervals

        #hide previous layout
        self.instruction_label.place_forget()
        self.next_button.place_forget()
        self.title_w.place_forget()

        self.background_label.place_forget()
        self.background_label.place(x = 0, y =0, relwidth = 1, relheight = 1)

        #add title again
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")

        #draw background rectangle
        self.static_width = 800
        self.rectangle = Canvas(self.background_label, bg = self.background, width = self.static_width, height = 150)
        self.rectangle.place(relx = 0.5, rely = 0.4, anchor = "center")
        
        #draw first moving rectangle
        self.variable_width = 0
        self.rectangle_variable = Canvas(self.rectangle, bg = self.my_yellow, width = self.variable_width, height = 150)
        self.rectangle_variable.place(relx = 0, rely = 0)

        #draw first breathing instruction 
        self.instruction_widget = Label(self.background_label, textvariable = self.breathing_instruction, font = ("Helvetica", 65), background = self.background, foreground = self.my_yellow)
        self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
        
        #measure initial time
        self.initial_time = time.time()
        #call meque no botãthod that will start iterative updates
        self.master.bind("<d>", self.delete_this) #delete this!!
        self.move_rectangle()

    def hrv_clear_rectangles(self):
        #this function was developed later, that's why it's not used everywhere
        self.rectangle.place_forget()
        self.rectangle_variable.place_forget()
        self.instruction_widget.place_forget()
        self.title_w.place_forget()

    def hrv_place_rectangles(self):
        self.background_label.place(x = 0, y =0, relwidth = 1, relheight = 1)
        self.rectangle.place(relx = 0.5, rely = 0.4, anchor = "center")
        
        self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
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
                self.breathing_instruction.set("EXPIRE")
                self.instruction_widget.place_forget()
                self.instruction_widget.config(foreground = self.my_blue)
                self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
                self.title_w.place_forget()
                self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
                self.rectangle_variable.config(bg = self.my_blue)
                
            else:
                self.increase = True
                #update instruction widget
                self.breathing_instruction.set("INSPIRE")
                self.instruction_widget.place_forget()
                self.instruction_widget.config(foreground = self.my_yellow)
                self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
                self.title_w.place_forget()
                self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
                self.rectangle_variable.config(bg = self.my_yellow)
        #Either way, increase or decrease is proportional to time left for 5 seconds
        if(self.increase):
            self.rectangle_variable.place_forget()

            #width increase
            self.variable_width = (self.static_width / self.breathing_interval) * (actual_time - self.iteration_start_time)
            #Shift growth direction
            if self.variable_width > 800: 
                self.variable_width = 800
                self.increase = False
                self.iteration_start_time = time.time()
                #update instruction widget
                self.breathing_instruction.set("INSPIRE")
                self.instruction_widget.place_forget()
                self.instruction_widget.config(foreground = self.my_yellow)
                self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
                self.title_w.place_forget()
                self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
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
                self.breathing_instruction.set("EXPIRE")
                self.instruction_widget.place_forget()
                self.instruction_widget.config(foreground = self.my_blue)
                self.instruction_widget.place(relx = 0.5, rely = 0.65, anchor = "center")
                self.title_w.place_forget()
                self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
                self.rectangle_variable.config(bg = self.my_blue)
        
        #call functions to draw the new rectangle
        self.rectangle_variable.place_forget()
        self.rectangle_variable.config(width = self.variable_width)
        self.rectangle_variable.place(relx = 0, rely = 0)

        #after the update, check if the total experiment time was acchieved
        if actual_time - self.initial_time > self.total_duration:
            #move on to next test. Call method that starts PVT
            self.active = False
            self.start_pvt()

    def layout_baseline(self):
        #clear layout
        self.hrv_clear_rectangles()
        #set new layout
        self.title_w.place(relx = 0.5, rely = 0.20, anchor = "center")
        #self.title_w.config
        self.relaxation_widget = Label(self.background_label, text = "TENTE PERMANECER RELAXADO.", font = ("Helvetica", 30), background = self.background, foreground = self.my_yellow)
        self.relaxation_widget2 = Label(self.background_label, text = "IREMOS COMEÇAR DENTRO DE APROXIMADAMENTE UM MINUTO." , font = ("Helvetica", 22), background = self.background, foreground = self.my_yellow)
        self.relaxation_widget.place(relx = 0.5, rely = 0.40, anchor = "center")
        self.relaxation_widget2.place(relx = 0.5, rely = 0.65, anchor = "center")
    
    def delete_this(self, event = None):
        self.initial_time = time.time() - 50

    def move_rectangle(self):
        now = time.time()
        if self.active:
            if (now - self.initial_time) < 60:
                #the first minute is just to measure baseline and relax
                if self.baseline == True:
                    self.layout_baseline()
                    self.baseline = False
                
            else:
                if self.baseline == False:
                    self.relaxation_widget.place_forget()
                    self.relaxation_widget2.place_forget()
                    self.hrv_clear_rectangles()
                    self.hrv_place_rectangles()
                    self.baseline = True #this is just to not verify this condition anymore. this will only run one time, and it's to set the first layout...
                    self.iteration_start_time = time.time()

                self.rectangle_update()
            
            self.call_identifier = self.master.after(20, self.move_rectangle)
    
    def start_pvt(self, event = None):
        self.experimentTimestamps.add_entry("t3", time.perf_counter())
        #make sure that hrv part has finished
        self.active = False

        #associate <s> key to skip this part of the test
        #self.master.bind("<s>", *nextmethod*)

        #clear screen
        self.rectangle.place_forget()
        self.rectangle_variable.place_forget()
        self.instruction_widget.place_forget()
        self.title_w.place_forget()
        self.relaxation_widget.place_forget()
        self.relaxation_widget2.place_forget()

        #set new title and instruction
        self.title_string.set("Tempo de Reação")
        self.instruction_string.set("No ecrã seguinte, será apresentado um rectângulo de cor verde. \n Sempre que a cor mudar para vermelho, clique no botão esquerdo do rato.\n\n Caso tenha alguma questão, não hesite em perguntar.")
        
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.4, anchor = "center")

        self.next_button['command'] = lambda: self.pvt_test()
        self.next_button.place(relx = 0.5, rely = 0.60, anchor = "center")
    
    def pvt_test(self):
        self.experimentTimestamps.add_entry("t4", time.perf_counter())
        self.pvt_tries = 5
        self.pvt_counter = 0
        self.pvt_active = False
        self.pvt_green = "#20E820"
        self.pvt_red =  "#ED1F1F"
        self.switch_time = {'0': 5, '1': 7, '2': 3, '3': 10, '4': 5}

        #associate <s> key to skip pvt test
        self.master.bind("<s>", self.signature_instruction_layout)

        #bind mouse1 to click
        self.master.bind("<Button-1>", self.pvt_click_detected)

        #configure screen layout
        self.next_button.place_forget()
        self.instruction_label.place_forget()
        self.title_w.place_forget()

        self.pvt_box = Canvas(self.background_label, bg = self.pvt_green, width = 800, height = 300)
        self.pvt_box.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.breathing_instruction.set("PREPARE-SE")
        self.instruction_widget.config(foreground = self.my_yellow, font = ("Helvetica", 50))
        self.instruction_widget.place(relx = 0.5, rely = 0.70, anchor = "center")
        self.title_w.place(relx = 0.5, rely = 0.10, anchor = "center")

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
            self.title_w.place_forget()
            self.title_w.place(relx = 0.5, rely = 0.1, anchor = "center")
            self.instruction_widget.place_forget()
            self.instruction_widget.place(relx = 0.5, rely = 0.70, anchor = "center")
            self.pvt_active = True

            self.pvt_box.place_forget()
            self.pvt_box.config(bg = self.pvt_red)
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
            self.pvt_iteration_start_time = time.perf_counter()
            self.reaction_end_time = None
            self.experimentTimestamps.add_entry("PVT_MISTAKE", "MISTAKE")
        else:
            self.reaction_time = self.reaction_end_time - self.reaction_ini_time
            
            print('Reaction time number ', self.pvt_counter)
            self.experimentTimestamps.add_entry("reaction_" + str(self.pvt_counter), str(self.reaction_time))
            self.experimentTimestamps.add_entry("t4" + str(2*self.pvt_counter), self.reaction_ini_time)
            self.experimentTimestamps.add_entry("t4" + str(2*self.pvt_counter + 1), self.reaction_end_time)

            #restore control variables and layout
            self.title_w.place_forget()
            self.title_w.place(relx = 0.5, rely = 0.1, anchor = "center")
            self.pvt_box.place_forget()
            self.pvt_box.config(bg = self.pvt_green)
            self.pvt_box.place(relx = 0.5, rely = 0.4, anchor = "center")
            self.instruction_widget.place_forget()
            self.instruction_widget.place(relx = 0.5, rely = 0.70, anchor = "center")
            self.pvt_active = False
            self.pvt_counter = self.pvt_counter + 1

            self.pvt_iteration_start_time = time.perf_counter()
            self.pvt_iteration()

    def signature_instruction_layout(self, event = None):
        self.experimentTimestamps.add_entry("t5", time.perf_counter())

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
        self.title_w.place_forget()
        self.pvt_box.place_forget()
        self.instruction_widget.place_forget()
        self.next_button.place_forget()
        
        #set new layout
        self.title_string.set("Assinatura")
        self.instruction_string.set("Nesta parte receberá uma folha em branco, que deverá assinar " + repr(self.number_signatures) + " vezes.\n\n De cada vez que terminar uma assinatura, deverá parar e clicar num botão de contagem que estará na página seguinte. \n\n Caso tenha alguma questão não hesite em perguntar.")
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.4, anchor = "center")

        self.next_button['command'] = lambda: self.signature_test()
        self.next_button.place(relx = 0.5, rely = 0.6, anchor = "center")

    def signature_test(self):
        self.experimentTimestamps.add_entry("t6", time.perf_counter())


        #change layout
        self.instruction_label.place_forget()
        self.title_w.place_forget()
        self.instruction_string.set("Deve incrementar o contador abaixo sempre que terminar uma assinatura.")
        self.breathing_instruction.set("NÚMERO DE ASSINATURAS OBTIDAS: " + repr(self.signature_counter))
        self.button_string.set("Incrementar")

        self.instruction_widget.config(fg = self.pvt_green, font = ("Helvetica", 40))
        self.next_button['command'] = lambda: self.signature_increment()
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.3, anchor = "center")
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.7, anchor = "center")
        
    def signature_increment(self):
        self.experimentTimestamps.add_entry("t6" + str(self.signature_counter), time.perf_counter())
        self.signature_counter = self.signature_counter + 1

        self.clear_screen()
        self.breathing_instruction.set("NÚMERO DE ASSINATURAS OBTIDAS: " + repr(self.signature_counter))
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.3, anchor = "center")
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.7, anchor = "center")

        if self.signature_counter == self.number_signatures:
            #call next method
            self.cognitive_tests_layout()

    def cognitive_tests_layout(self):
        self.experimentTimestamps.add_entry("t7", time.perf_counter())

        #clear screen
        self.clear_screen()

        self.title_string.set("Trail Making Test - Parte A")
        self.instruction_string.set("Nesta parte irá receber uma folha que contém diversas bolas numeradas. \n\n O objetivo é unir as diversas bolas de forma sequencial, o mais rapidamente possível e sem cometer erros. \n\n Caso tenha alguma dúvida não hesite em perguntar.")
        self.button_string.set("Começar")
        self.next_button['command'] = lambda: self.start_trail_making_a()

        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.6, anchor = "center")

    def start_trail_making_a(self):
        self.experimentTimestamps.add_entry("t8", time.perf_counter())

        self.clear_screen()

        self.instruction_string.set("Quando terminar o teste, clique no botão abaixo.")
        self.button_string.set("Terminado")
        self.next_button['command'] = lambda: self.prepare_trail_making_b()
        self.add_common_widgets()

        self.ini_time_tma = datetime.now()
        
    def prepare_trail_making_b(self):
        self.experimentTimestamps.add_entry("t9", time.perf_counter())

        self.end_time_tma = datetime.now()
        dif = self.end_time_tma - self.ini_time_tma
        print("TRAIL MAKING A: Demorou " + repr(dif.seconds) + " a completar a primeira parte do teste.")

        self.clear_screen()

        self.title_string.set("Trail Making Test - Parte B")
        self.instruction_string.set("Nesta parte irá receber uma folha que contém diversas bolas, com números ou letras. \n\n O objetivo é unir as diversas bolas de forma sequencial, o mais rapidamente possível e sem cometer erros. \n \n Tenha em consideração que por exemplo a letra B é equivalente ao número 2. \n\n Caso tenha alguma dúvida não hesite em perguntar.")
        self.button_string.set("Começar")
        self.next_button['command'] = lambda: self.start_trail_making_b()

        self.add_common_widgets()
    
    def start_trail_making_b(self):
        self.experimentTimestamps.add_entry("t10", time.perf_counter())

        self.clear_screen()

        self.instruction_string.set("Quando terminar o teste, clique no botão abaixo.")
        self.button_string.set("Terminado")
        self.next_button['command'] = lambda: self.store_end_time_tmb()
        
        self.add_common_widgets()

        self.ini_time_tmb = datetime.now()

    def store_end_time_tmb(self):
        self.experimentTimestamps.add_entry("t11", time.perf_counter())
        self.end_time_tmb = datetime.now()

        dif = self.end_time_tmb - self.ini_time_tmb
        
        print("TRAIL MAKING B: Demorou " + repr(dif.seconds) + " a completar a primeira parte do teste.")

        self.physical_tests_layout()

    def physical_tests_layout(self):
        self.clear_screen()

        self.title_string.set("Testes físico")
        self.instruction_string.set("Para esta parte deverá colocar a pulseira no seu braço não dominante. \n\n De seguida será explicado os exercícios que deverá efectuar.")
        self.button_string.set("Iniciar")
        self.next_button['command'] = lambda: self.start_physical_tests()
        self.add_common_widgets()
        
    def start_physical_tests(self):
        self.experimentTimestamps.add_entry("t12", time.perf_counter())
        self.ini_time_physical = datetime.now()

        self.physical_tests_counter = 0
        self.number_physical_tests = 5

        self.clear_screen()
        self.breathing_instruction.set("NÚMERO DE VOLTAS TERMINADAS: " + repr(self.physical_tests_counter))
        self.instruction_string.set("Clique no botão abaixo sempre que uma volta for completada")

        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.3, anchor = "center")
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.7, anchor = "center")

       
        self.button_string.set("Incrementar")
        self.next_button['command'] = lambda: self.physical_increment()

        #self.add_common_widgets()

    def physical_increment(self, event = None):
        self.experimentTimestamps.add_entry("t12" + str(self.physical_tests_counter), time.perf_counter())
        self.physical_tests_counter = self.physical_tests_counter + 1

        self.clear_screen()
        self.breathing_instruction.set("NÚMERO DE VOLTAS TERMINADAS: " + repr(self.physical_tests_counter))
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.3, anchor = "center")
        self.instruction_widget.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.7, anchor = "center")

        if self.physical_tests_counter == self.number_physical_tests:
            #call next method
            self.store_end_time_physical()   

    def store_end_time_physical(self):
        self.experimentTimestamps.add_entry("t13", time.perf_counter())
        self.end_time_physical = datetime.now()
        dif1 = self.end_time_physical - self.ini_time_physical
        self.thank_you_layout()


    def thank_you_layout(self):
        self.clear_screen()
        self.title_string.set("Muito obrigado pelo seu contributo!")
        self.button_string.set("Exportar dados")
        self.next_button['command'] = lambda: self.export_time_intervals()
        
        self.title_w.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.7, anchor = "center")
        #ADD LOGOS OF ISR and HBA

    def export_time_intervals(self):
        #prompt for patient name in 
        self.patient_name = input("Escreva o nome do paciente: ")
        filename = self.patient_name + "_" + str(self.experimentTimestamps.epoch)

        filename = filename.replace(" ", "_")
        filename = filename.replace(":", "-")
        filename = filename.replace(".", "-")
    

        print("Name of file %s", filename)
        
        with open(filename + '.json', "w") as fp:
            json.dump(self.experimentTimestamps.stamp_dict, fp)


    def add_common_widgets(self):
        self.title_w.place(relx = 0.5, rely = 0.2, anchor = "center")
        self.instruction_label.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.next_button.place(relx = 0.5, rely = 0.6, anchor = "center")

    def clear_screen(self):
        self.title_w.place_forget()
        self.instruction_label.place_forget()
        self.next_button.place_forget()
        self.instruction_widget.place_forget()


class experimentTimeObject:
    #This class contains a dictionary (stamp_dict) to keep track of the time intervals corresponding to the different tests
    
    def __init__(self, time, date, epoch):
        #store initial stamp: number of seconds since epoch, that should be used to sync with the wristband timestamp
        self.initial_stamp = time
        self.start_date = date
        self.epoch = epoch
        #note: perf_counter is not to measure absolute time. only differences between them have value
        
        self.stamp_dict = {'t1': time, 'timestamp': str(date), 'epoch': epoch}
        
        print("t1: ", self.stamp_dict['t1'])
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
