import sqlite3

def whatever():
    conn = sqlite3.connect('my_db.db')

    print("hello world")
    print("Result of creating db: %s", str(conn))

    cursor = conn.cursor()

    # 1 - relational tables implementation
    # 1.1 - table: Doctor(id, name)

    cursor.execute("CREATE TABLE doctor(doctor_id, doctor_name)")

    cursor.execute("INSERT INTO doctor VALUES ('1', 'Miguel Constante')")

    result = cursor.execute('SELECT * from doctor')

    for row in result:
        print(row)

def create_connection(db_file):
    #db_file: points to SQLite database
    #return: connection object or None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def create_table(conn, create_table_sql):
    #conn: connection object to database
    #create_table_sql: a create table statement

    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = "C:\Users\Naim\Desktop\Tese\Programming\Acquisition\my_database.db"

    sql_create_doctor_table = """ CREATE TABLE IF NOT EXISTS doctor (
                                    doctor_id integer PRIMARY KEY,
                                    doctor_name text NOT NULL
                                    );"""

    sql_create_patient_table = """ CREATE TABLE IF NOT EXISTS patient (
                                    patient_id integer PRIMARY KEY,
                                    patient_name text NOT NULL
                                    );"""

    sql_create_datafile_table = """ CREATE TABLE IF NOT EXISTS datafile (
                                    file_name integer PRIMARY KEY,
                                    patient_id integer NOT NULL,
                                    FOREIGN KEY (patient_id) REFERENCES patient(patient_id) 
                                    );"""
    
    #sql_create_timings_table = """ CREATE TABLE IF NOT EXISTS timing (

 

