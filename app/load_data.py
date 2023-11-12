import pandas as pd
from app.gapi.tools import import_impedances_db

data = {}
data["catalogue"] = import_impedances_db('Catalogue!A4:J')
data["impedances"] = import_impedances_db('Impedance Measurement!A3:Q')

data["catalogue"]["Last Measured Date"] = pd.to_datetime(data["catalogue"]["Last Measured Date"], format="%b %d %Y")
data["impedances"]["Measured Date"] = pd.to_datetime(data["impedances"]["Measured Date"], format="%b %d %Y")

data["mea tags"] = list(data["catalogue"]["Tag Number"])


assert data["catalogue"] is not None, "Failed to import data from Google Sheets: catalogue"
assert data["impedances"] is not None, "Failed to import data from Google Sheets: impedance"
