import pandas as pd

df = pd.read_csv("final_dataset.csv")

# Group observations by location, weather, and hour
aggregated = (
    df.groupby(
        [
            "lat",
            "lng",
            "temperature",
            "humidity",
            "wind_speed",
            "hour"
        ]
    )["howMany"]
    .sum()
    .reset_index()
)

aggregated.rename(
    columns={"howMany": "total_birds"},
    inplace=True
)

print(aggregated.head())

aggregated.to_csv(
    "aggregated_dataset.csv",
    index=False
)

print("\nSaved aggregated_dataset.csv")
print("Shape:", aggregated.shape)