import streamlit as st
import pickle
import numpy as np
import pandas as pd
import pydeck as pdk

# Page Configuration
st.set_page_config(
    page_title="AeroBird | Bird Density Prediction Dashboard",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    /* CSS hacks for styling Streamlit */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1 {
        font-weight: 800;
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #1E293B;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 2.25rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .metric-label {
        font-size: 0.875rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""", unsafe_allow_html=True)

# Load Model
@st.cache_resource
def load_prediction_model():
    with open("models/bird_density_model.pkl", "rb") as f:
        return pickle.load(f)

# Load Aggregated Dataset for Visualization
@st.cache_data
def load_historical_data():
    return pd.read_csv("aggregated_dataset.csv")

model = load_prediction_model()
df_historical = load_historical_data()

# Header Section
col_title, col_logo = st.columns([8, 1])
with col_title:
    st.title("🦅 AeroBird Density Prediction")
    st.markdown(
        "Deploying **Extra Trees Machine Learning** aligned with real-time historical weather to forecast avian abundance."
    )

st.divider()

# Layout: Sidebar Inputs and Main Dashboard
with st.sidebar:
    st.header("⚙️ Environmental Inputs")
    st.markdown("Adjust parameters to simulate local environment conditions.")

    latitude = st.number_input(
        "Latitude",
        min_value=-90.0,
        max_value=90.0,
        value=18.5418,
        format="%.4f",
        help="Target geographic latitude."
    )

    longitude = st.number_input(
        "Longitude",
        min_value=-180.0,
        max_value=180.0,
        value=73.7276,
        format="%.4f",
        help="Target geographic longitude."
    )
    
    st.divider()

    temperature = st.slider(
        "Temperature (°C)",
        min_value=-10,
        max_value=50,
        value=28,
        help="Local temperature in degrees Celsius."
    )

    humidity = st.slider(
        "Humidity (%)",
        min_value=0,
        max_value=100,
        value=65,
        help="Relative atmospheric humidity percentage."
    )

    wind_speed = st.slider(
        "Wind Speed (km/h)",
        min_value=0,
        max_value=100,
        value=12,
        help="Wind speed in kilometers per hour."
    )

    hour = st.slider(
        "Time of Day (Hour)",
        min_value=0,
        max_value=23,
        value=11,
        format="%02d:00",
        help="Simulated time of observation (24-hour format)."
    )

# Dashboard Content
tab1, tab2 = st.tabs(["📊 Live Prediction", "🗺️ Historical Activity Map"])

with tab1:
    col_metrics, col_info = st.columns([1, 1])
    
    with col_metrics:
        st.subheader("Simulated Prediction")
        
        # Feature processing
        hour_sin = np.sin(2 * np.pi * hour / 24.0)
        hour_cos = np.cos(2 * np.pi * hour / 24.0)
        
        features = np.array([
            [
                latitude,
                longitude,
                temperature,
                humidity,
                wind_speed,
                hour,
                hour_sin,
                hour_cos
            ]
        ])
        
        prediction = max(0.0, model.predict(features)[0])
        
        # Risk/Density Categorization
        if prediction < 3.0:
            status_color = "🟢"
            status_label = "Low Activity"
            status_class = "success"
        elif prediction < 10.0:
            status_color = "🟡"
            status_label = "Moderate Activity"
            status_class = "warning"
        else:
            status_color = "🔴"
            status_label = "High Activity"
            status_class = "error"
            
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">Predicted Bird Density</div>
                <div class="metric-value">{prediction:.2f} <span style="font-size: 1.2rem; color: #94A3B8;">birds / area</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Activity Status</div>
                <div class="metric-value">{status_color} {status_label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
    with col_info:
        st.subheader("Environment Summary")
        st.info(
            f"""
            📍 **Coordinates:** {latitude:.4f}, {longitude:.4f}  
            ⏰ **Observation Time:** {hour:02d}:00  
            🌡️ **Temperature:** {temperature}°C  
            💧 **Relative Humidity:** {humidity}%  
            💨 **Wind Speed:** {wind_speed} km/h  
            """
        )
        
        # Quick summary helper
        st.write(
            f"At {hour:02d}:00, under {temperature}°C temperatures and {wind_speed} km/h winds, "
            f"the model predicts an expected density of **{prediction:.1f}** birds per checklist area."
        )

with tab2:
    st.subheader("Bird Observation Densities Across India")
    st.markdown("Below is a spatial distribution mapping of eBird coordinates and their aggregated bird sightings count.")
    
    # Check if data coordinates are available
    if not df_historical.empty:
        # Construct pydeck Map
        view_state = pdk.ViewState(
            latitude=df_historical["lat"].mean(),
            longitude=df_historical["lng"].mean(),
            zoom=4.5,
            pitch=30
        )
        
        # Normalize size scaling for visualization
        df_visual = df_historical.copy()
        df_visual["size_scaled"] = df_visual["total_birds"] * 1000
        
        layer = pdk.Layer(
            "ScatterplotLayer",
            df_visual,
            get_position=["lng", "lat"],
            get_color="[255, 107, 107, 160]",
            get_radius="size_scaled",
            radius_min_pixels=5,
            radius_max_pixels=40,
            pickable=True
        )
        
        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={"text": "Location: ({lat}, {lng})\nTotal Birds Seen: {total_birds}"}
        ))
    else:
        st.warning("Historical dataset is empty or could not be loaded.")

# Footer section
st.divider()
st.caption(
    "Built using eBird API • Open-Meteo Historical Weather API • Extra Trees Regressor • Streamlit Web Dashboard"
)