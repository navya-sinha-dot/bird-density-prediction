import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.metrics import r2_score, mean_absolute_error, root_mean_squared_error

# Load dataset
df = pd.read_csv("aggregated_dataset.csv")

# Remove rows with missing values
df = df.dropna()

# Cyclical feature engineering for hour
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24.0)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24.0)

# Features
features = [
    "lat",
    "lng",
    "temperature",
    "humidity",
    "wind_speed",
    "hour",
    "hour_sin",
    "hour_cos"
]
X = df[features]

# Target
y = df["total_birds"]

# Split data for metric tracking
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train the best ExtraTreesRegressor model found by hyperparameter search
model = ExtraTreesRegressor(
    n_estimators=50,
    max_depth=3,
    max_features="sqrt",
    min_samples_leaf=4,
    min_samples_split=2,
    random_state=42
)

model.fit(X_train, y_train)

# Predictions
preds = model.predict(X_test)

# Metrics
r2 = r2_score(y_test, preds)
mae = mean_absolute_error(y_test, preds)
rmse = root_mean_squared_error(y_test, preds)

print("\nMODEL EVALUATION RESULTS (Test Set)")
print("R2 Score :", r2)
print("MAE      :", mae)
print("RMSE     :", rmse)

# Train on the complete dataset for final deployment
print("\nTraining final model on full dataset...")
final_model = ExtraTreesRegressor(
    n_estimators=50,
    max_depth=3,
    max_features="sqrt",
    min_samples_leaf=4,
    min_samples_split=2,
    random_state=42
)
final_model.fit(X, y)

# Save final model
with open("models/bird_density_model.pkl", "wb") as f:
    pickle.dump(final_model, f)

print("Final model saved successfully to models/bird_density_model.pkl")