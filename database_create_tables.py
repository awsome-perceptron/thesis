import sqlite3
import json
from pprint import pprint

timings = json.load(open('hello__2018-03-13_17_17_56.json')) 

pprint(timings)
print("hello world")
print(timings['timestamp']) 