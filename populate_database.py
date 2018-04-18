import sqlite3
import json
from pprint import pprint

#table names: doctor, patient, datafile, timings
    
class timingsObject:
    #parses the .json generated on acquisition step. It will calculate and store the indexes (respective to the corresponding empatica e4 datafile) corresponding to the different exercises.    
    def __init__(self, timings_file):
        self.input = json.load(open(timings_file))
        self.timestamp = self.input['timestamp']
        self.reference = self.input['t1']
        #the following dictionary will have as key the name of the experiment and as values the begin and end time (in reference to the first time)
        self.intervals = {}

    def create_intervals(self):
        #breathing: between t2 and t3
        self.add_entry("breathing", 't2', 't3')
        #reaction_time: between t4 and t5
        self.add_entry("reaction_time", 't4', 't5')
        #signature: between t6, t7
        self.add_entry("signature", 't6', 't7')
        #tma: between t8, t9
        self.add_entry("tma", 't8', 't9')
        #tmb: between t10,t11
        self.add_entry("tmb", 't10', 't11')
        #physical: between t12,13
        self.add_entry("physical", 't12', 't13')

    def add_entry(self, exercise, index1, index2):
        self.intervals[exercise] = {'begin': self.input[index1] - self.reference, 'end': self.input[index2] - self.reference}


timings = timingsObject("hello__2018-03-13_17_17_56.json")

pprint(timings.input)
print("%%%%%%%%%%%%% End of the input file %%%%%%%%%%%")
timings.create_intervals()
print("%%%%%%%%%%%% ABSOLUTE INTERVALS %%%%%%%%%%%%%%%")
pprint(timings.intervals)

