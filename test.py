import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from separation_indexes_calculation import empaticaParser
from matplotlib.widgets import Slider
import numpy as np

SAMPLE_RATES = {'ACC': 32, 'BVP': 64, 'EDA': 4, 'TEMP': 4, 'HR': 1}

def display_experiment(empaticaObject):
    counter = 0

    plt.figure()

    for signal in empaticaObject.data.keys():
        if signal == "IBI":
            continue

        counter = counter + 1

        data = empaticaObject.data[signal]
        (tempo, step) = np.linspace(0, len(data)/SAMPLE_RATES[signal], num = len(data), endpoint = False, retstep = True)

        new_figure = plt.subplot(int("51" + repr(counter)))
        new_figure.plot(tempo, data)
        new_figure.set_xlabel("Samples")
        new_figure.set_ylabel(signal)

    plt.show()



if __name__ == "__main__":
    folder =  "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data\\D1\\1"
    e4_file = "1523979808_A01251"

    empaticaObject = empaticaParser(folder, e4_file)


    counter = 0

    plt.figure()

    for signal in empaticaObject.data.keys():
        if signal == "IBI":
            continue

        counter = counter + 1

        data = empaticaObject.data[signal]
        (tempo, step) = np.linspace(0, len(data)/SAMPLE_RATES[signal], num = len(data), endpoint = False, retstep = True)

        new_figure = plt.subplot(int("51" + repr(counter)))
        new_figure.plot(tempo, data)
        new_figure.set_xlabel("Samples")
        new_figure.set_ylabel(signal)


