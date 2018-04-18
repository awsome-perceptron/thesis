import time
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import csv
import os
from pprint import pprint

def data_as_float(file, n_columns):
    #input: E4's csv filess
    #output: pandas series structure with input as floats
    with open(file, 'r') as raw:
        lines = raw.readlines()

    input_as_float = np.zeros((len(lines),dimension), dtype = float)

    for i in range(len(lines)):
        lines[i] = lines[i].replace('\n', '')
        lines[i] = lines[i].split(',')
        input_as_float[i] = np.asarray(lines[i], dtype = float)

    return pd.DataFrame(input_as_float)
   
session_folder = "1520961448_A01251"

#open accelerometer file
file_ = "/ACC_test.csv"
acc_file = session_folder + file_

#s = pd.Series(lines, dtype = float)
#df = pd.DataFrame(s)

a = actigraphy_as_array(acc_file)
