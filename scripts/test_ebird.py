import os
import requests
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

print("Status Code:", response.status_code)

data = response.json()

print("\nNumber of records:", len(data))

print("\nFirst record:")
print(data[0])