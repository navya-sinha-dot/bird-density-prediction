import requests

lat = 18.541881
lon = 73.72766

url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}"
    f"&longitude={lon}"
    f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
)

response = requests.get(url)

data = response.json()

print(data)