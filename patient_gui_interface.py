from tkinter import *
from tkinter.font import Font
import sqlite3
import time

#database functions
def open_db_connection():
    db = sqlite3.connect('my_database')
    return db

def close_db_connection(db):
    db.close()

def create_patient_table(db):
    cursor = db.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS patient(id TEXT PRIMARY KEY, name TEXT, epoch INTEGER)'''
    cursor.execute(sql)
    db.commit()

def create_session_table(db):
    cursor = db.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS session(number TEXT, session_name TEXT,
            epoch INTEGER, patient_id TEXT, timings_name TEXT,  
            PRIMARY KEY(number,patient_id),
            FOREIGN KEY(patient_id) REFERENCES patient(id)
            )'''
    cursor.execute(sql)
    db.commit()

def drop_table(db, table_name):
    cursor = db.cursor()
    sql = "DROP TABLE IF EXISTS " + table_name
    cursor.execute(sql)
    db.commit()

def insert_patient(db, p_id, p_name, p_epoch):
    cursor = db.cursor()
    sql = '''INSERT INTO patient(id, name, epoch) VALUES(?,?,?)'''
    cursor.execute(sql, (p_id, p_name, p_epoch))
    print("User " + p_name + " inserted!")
    db.commit()

def insert_session(db, number, session_name, epoch, patient_id, timings_name):
    cursor = db.cursor()
    sql = '''INSERT INTO session(number, session_name, epoch, patient_id, timings_name) VALUES (?,?,?,?,?)'''
    cursor.execute(sql, (number, session_name, epoch, patient_id, timings_name))
    print("Session " + number + " from " + patient_id + " inserted!")
    db.commit()

def display_patients(db):
    cursor = db.cursor()
    cursor.execute('''SELECT id, name FROM patient''')
    all_rows = cursor.fetchall()
    for row in all_rows:
        print('{0} : {1}'.format(row[0],row[1]))

def display_sessions(db):
    cursor = db.cursor()
    cursor.execute('''SELECT number, patient_id
                    FROM session''')
    all_rows = cursor.fetchall()
    for row in all_rows:
        print('{0}: {1}'.format(row[0],row[1]))

def populate_tables(db):
    insert_patient(db, "H1", "Rita Oliveira", int(time.time()))
    insert_patient(db, "H_INV", "John Doe", int(time.time()))

    insert_session(db, "Experiment 1", "1656545646_DEVICE_SNUM", int(time.time()), "H1", "TIMINGS_FILE_NAME")
    insert_session(db, "Experiment 2", "165654456456_DEVICE_SNUM", int(time.time()), "H1", "TIMINGS_FILE_NAME")
    insert_session(db, "Experiment 3", "16565456456_DEVICE_SNUM", int(time.time()), "H1", "TIMINGS_FILE_NAME")

    insert_session(db, "Experiment 1", "165654566456_DEVICE_SNUM", int(time.time()), "H_INV", "TIMINGS_FILE_NAME")
    insert_session(db, "Experiment 2", "1656545646456_DEVICE_SNUM", int(time.time()), "H_INV", "TIMINGS_FILE_NAME")

def drop_all_tables(db):
    drop_table(db, "patient")
    drop_table(db, "session")


#DATABASE CREATION
db = open_db_connection()

drop_all_tables(db)
create_patient_table(db)
create_session_table(db)

populate_tables(db)

display_patients(db)
display_sessions(db)

#USER INTERFACE
root = Tk()
frame = Frame(root)
frame.pack(fill = "both" , expand = "yes")

#FONT TO BE USED IN BUTTONS
helv36 = Font(family='Helvetica', size=36)

bottom_frame = Frame(root)
bottom_frame.pack(fill = "both" , expand = "yes")

add_patient_button = Button(frame, text = "ADD PATIENT", fg = "white", bg = "grey", font = helv36)
add_patient_button.pack(fill = "both" , expand = "yes")

add_experiment_button = Button(bottom_frame, text = "ADD EXPERIMENT", fg = "white", bg = "grey", font = helv36)
add_experiment_button.pack(fill = "both" , expand = "yes")


root.mainloop()



