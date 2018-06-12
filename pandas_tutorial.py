import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import datetime

if __name__ == "__main__":
    time_list = []
    
    for i in range(10):
        time_list.append(datetime.datetime.strptime((repr(i+1) + "/04/2018 16:15:15"), "%d/%m/%Y %H:%M:%S"))
        time_list.append(datetime.datetime.strptime(repr(i + 15) + "/03/2018 16:15:15", "%d/%m/%Y %H:%M:%S"))

    for item in time_list:
        print(item) 

    