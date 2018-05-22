from __future__ import print_function
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import pandas as pd
import json

SCOPE = ["https://spreadsheets.google.com/feeds"]
SECRETS_FILE = "Fetch Panas Data-1e6adbfc020b.json"
SPREADSHEET = "Escala de Afecto Positivo e Negativo - HBA (respostas)"

json_key = json.load(open(SECRETS_FILE))

credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], SCOPE)
