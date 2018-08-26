from session import CompleteSession
import matplotlib.pyplot as plt
import global_variables as gv
import os
from empatica import empaticaParser
from timings import timingsParser
from panas import panasParser
import time


if __name__ == "__main__":
    sessionList = []
    counter = 0

    sessionList2 = []
    counter2 = 0

    ini_time = time.perf_counter()

    for patient in os.listdir(gv.BASE_FOLDER):
        if patient == "D5":
            continue

        folder = gv.BASE_FOLDER + patient
        for experiment in os.listdir(folder):
            print("Run - {}-{}".format(patient, experiment))
            sessionObject = CompleteSession(patient, int(experiment), False)
            sessionList.append(sessionObject)
            counter += 1

    end_time = time.perf_counter()
    print("Time for first run: {}".format(end_time - ini_time))



