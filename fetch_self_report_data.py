from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import pandas as pd
import numpy as np
import os

POSITIVE_AFFECT = ["Interessado", "Excitado", "Agradavelmente surpreendido", "Caloroso", "Entusiasmado", "Orgulhoso", "Encantado", "Inspirado", "Determinado", "Activo"]
NEGATIVE_AFFECT = ["Perturbado", "Atormentado", "Culpado", "Assustado", "Repulsa", "Irritado", "Remorsos", "Nervoso", "Tremulo", "Amedrontado"]
BASE_FOLDER = "C:\\Users\\Naim\\Desktop\\Tese\\Programming\\Data"

def parse_panas_data(sheet_values):
    #Remove header from data. This will be used as labels for the DataFrames
    headers = sheet_values.pop(0)

    for i in range(len(headers)):
        #Removal of some garbage
        headers[i] = headers[i].replace(' [', '')
        headers[i] = headers[i].replace(']', '')

    #Convert data from sheet to specific data types
    for line in sheet_values:
        line[2] = int(line[2])
        line[0] = datetime.datetime.strptime(line[0], "%d/%m/%Y %H:%M:%S")

        for i in range(len(line)):
            if i < 4:
                continue

            line[i] = int(line[i])

    data = pd.DataFrame(sheet_values, columns = headers)

    #Initialize Posite and Negativa affect columns. Note: data.shape[0] yields number of rows
    data['PA'] = pd.Series(np.zeros(data.shape[0]), dtype = int)
    data['NA'] = pd.Series(np.zeros(data.shape[0]), dtype = int)

    #Calculate Positive and Negative Affects
    for i in range(len(POSITIVE_AFFECT)):
        data['PA'] = data['PA'] + data[POSITIVE_AFFECT[i]]
        data['NA'] = data['NA'] + data[NEGATIVE_AFFECT[i]]


    #To be able to search the DataFrame by the patient ID, create an index
    data.set_index("ID", inplace = True)

    return data

def fetch_sheet_data():

    # Setup the Sheets API
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        flags = tools.argparser.parse_args(args=[])
        creds = tools.run_flow(flow, store, flags)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API to Fetch all data
    SPREADSHEET_ID = '1Wi2eezOzJ3VQcLSp-oyUJuGxFCiI-dz_I0FSqtwv37U'
    RANGE_NAME = 'A:X'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                range=RANGE_NAME).execute()

    #Values contains all the data from the sheet
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Stamp, ID, Interessado:')
        for row in values:
            # Print columns A and E, which correspond to indices 0 and 4.
            print('%s, %s, %s' % (row[0], row[1], row[4]))

    return values

def write_panas_json(dataframe, patient_id, experiment_number):
    destination_folder = BASE_FOLDER + "\\" + patient_id + "\\" + repr(experiment_number) + "\\panas_data.json"

    #fetch patient dataframe and sort it according to the timestamp
    patient_dataframe = dataframe.loc[patient_id]
    
    if len(patient_dataframe.shape) == 2:
        patient_dataframe = patient_dataframe.sort_values('Carimbo de data/hora')
        experiment_dataframe = patient_dataframe.iloc[experiment_number - 1]
    elif len(patient_dataframe.shape) == 1:
        experiment_dataframe = patient_dataframe

    experiment_dataframe['ID'] = patient_id

    #Write json (using dataframe existing method)
    experiment_dataframe.to_json(destination_folder, orient = "columns")

def write_all_json(dataframe):
    for patient_folder in os.listdir(BASE_FOLDER):
        print(patient_folder)
        for experiment_folder in os.listdir(BASE_FOLDER + "\\" + patient_folder):
            print(experiment_folder)
            write_panas_json(dataframe, patient_folder, int(experiment_folder))

if __name__ == "__main__":
    values = fetch_sheet_data()
    dataframe = parse_panas_data(values)

    #Execute this script to generate all the panas json files
    write_all_json(dataframe)







