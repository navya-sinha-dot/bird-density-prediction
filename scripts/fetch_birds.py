import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("EBIRD_API_KEY")

if not API_KEY:
    raise ValueError("EBIRD_API_KEY environment variable is not set. Please check your .env file.")

headers = {
    "X-eBirdApiToken": API_KEY
}

url = "https://api.ebird.org/v2/data/obs/IN/recent"

response = requests.get(url, headers=headers)

data = response.json()

df = pd.DataFrame(data)

df = df[
    [
        "comName",
        "howMany",
        "lat",
        "lng",
        "obsDt"
    ]
]

df.to_csv("birds.csv", index=False)

print(df.head())
print("\nSaved birds.csv")