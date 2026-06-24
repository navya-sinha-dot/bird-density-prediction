import pandas as pd
import requests
import time
import datetime

# Read bird observations
birds = pd.read_csv("data/birds.csv")

# Clean missing target values
birds = birds.dropna(subset=["howMany"])

# Convert obsDt to datetime
birds["obs_dt_parsed"] = pd.to_datetime(birds["obsDt"])
birds["date_str"] = birds["obs_dt_parsed"].dt.strftime("%Y-%m-%d")
birds["hour"] = birds["obs_dt_parsed"].dt.hour

# Round coordinates to 4 decimal places for robust weather matching
birds["lat_round"] = birds["lat"].round(4)
birds["lng_round"] = birds["lng"].round(4)

# Find unique date-location pairs
unique_pairs = birds.groupby(["date_str", "lat_round", "lng_round"]).size().reset_index()

print(f"Total bird observations: {len(birds)}")
print(f"Unique (date, lat, lng) combinations to fetch: {len(unique_pairs)}")

weather_map = {}

# Group by date to query all locations on that date in batch
grouped_by_date = unique_pairs.groupby("date_str")

for date_str, group in grouped_by_date:
    lats = group["lat_round"].tolist()
    lngs = group["lng_round"].tolist()
    
    # Chunk lats and lngs to max 50 locations per query (Open-Meteo limit)
    chunk_size = 50
    for idx in range(0, len(lats), chunk_size):
        chunk_lats = lats[idx:idx + chunk_size]
        chunk_lngs = lngs[idx:idx + chunk_size]
        
        lat_param = ",".join(map(str, chunk_lats))
        lng_param = ",".join(map(str, chunk_lngs))
        
        print(f"Fetching weather for {len(chunk_lats)} locations on {date_str}...")
        
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat_param}"
            f"&longitude={lng_param}"
            f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
            f"&start_date={date_str}"
            f"&end_date={date_str}"
            f"&timezone=auto"
        )
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # If only one location was queried, the API returns a dict instead of a list
                if isinstance(data, dict):
                    results_list = [data]
                else:
                    results_list = data
                
                for loc_idx, loc_data in enumerate(results_list):
                    lat_key = chunk_lats[loc_idx]
                    lng_key = chunk_lngs[loc_idx]
                    
                    hourly = loc_data.get("hourly", {})
                    times = hourly.get("time", [])
                    temps = hourly.get("temperature_2m", [])
                    hums = hourly.get("relative_humidity_2m", [])
                    winds = hourly.get("wind_speed_10m", [])
                    
                    # Store 24 hourly readings for this location and date
                    for h in range(24):
                        if h < len(temps):
                            weather_map[(lat_key, lng_key, date_str, h)] = (
                                temps[h],
                                hums[h],
                                winds[h]
                            )
            else:
                print(f"Failed to fetch: Status code {response.status_code}")
        except Exception as e:
            print(f"Error fetching weather: {e}")
            
        # Respect rate limits
        time.sleep(0.2)

# Align each observation in the dataset with its corresponding weather
temperatures = []
humidities = []
wind_speeds = []

for _, row in birds.iterrows():
    key = (row["lat_round"], row["lng_round"], row["date_str"], row["hour"])
    if key in weather_map:
        temp, hum, wind = weather_map[key]
        temperatures.append(temp)
        humidities.append(hum)
        wind_speeds.append(wind)
    else:
        # Fallback to hourly averages or None
        temperatures.append(None)
        humidities.append(None)
        wind_speeds.append(None)

birds["temperature"] = temperatures
birds["humidity"] = humidities
birds["wind_speed"] = wind_speeds

# Save the complete aligned dataset
birds.to_csv("final_dataset.csv", index=False)

print("\nDataset aligned and saved to final_dataset.csv")
print("Shape:", birds.shape)
print("Missing temperature values:", birds["temperature"].isna().sum())