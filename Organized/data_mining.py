from visualization import MultipleVisualization
from session import completeSession
import matplotlib.pyplot as plt
import global_variables as gv
import os
from empatica import empaticaParser
from timings import timingsParser
from panas import panasParser

if __name__ == "__main__":
    sessionList = []

    for patient in os.listdir(gv.BASE_FOLDER):
        folder = gv.BASE_FOLDER + patient
        for experiment in os.listdir(folder):
            print("{}- {}".format(patient, experiment))
            folder = gv.BASE_FOLDER + patient + "\\" + experiment

            # Creation of  Empatica, Timings and Panas objects
            empaticaObject = empaticaParser(folder)
            timingsObject = timingsParser(folder, empaticaObject.event_list[0], empaticaObject.stamps_dictionary, empaticaObject.rates_dictionary,
                                               empaticaObject.actigraphy_length)
            panasObject = panasParser(folder)
            #sessionObject = completeSession(patient, int(experiment))
            #sessionList.append(sessionObject)

    multiple_view = MultipleVisualization(sessionList)
    multiple_view.power_spectral_density()
    plt.plot()
