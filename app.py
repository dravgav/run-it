import streamlit as st
import openrouteservice
import pandas as pd

# openrouteservice api key initialization
ORS_API_KEY = st.secrets["openrouteservice"]["api_key"]
client = openrouteservice.Client(key=ORS_API_KEY)

# streamlit UI
st.title("Running Route Generator")

location = st.text_input("Enter your location address: ")
# use st.map so they can pinpoint it on the map later

unit = st.radio("Choose your preferred unit: ", ("km", "mi"))

if unit == "km": 
    min_dist = 1.0
    max_dist = 48.0
    step = 0.5
if unit == "mi":
    min_dist = 1.0
    max_dist = 30.0
    step = 0.5

distance = st.slider(f"Choose your preferred running distance ({unit.lower()}):",
                     min_value=min_dist, max_value=max_dist, value=5.0, step=step)
st.write(f"You selected a distance of {distance} {unit.lower()}.")

# since calculations using ors will be in meters
if unit == 'km':
    distance_meters = distance * 1000
else:
    distance_meters = distance * 1609.34

# Elevation options in meters
elevation_options = {
    'Mild (under 20m elevation change)': (0, 20),
    'Medium (21-50m elevation change)': (21, 50),
    'Challenging (51-100m elevation change)': (51, 100),
    'Extreme (over 100m elevation change)': (100, 1000)
}

elevation_choice = st.selectbox("Select your preferred elevation change:", list(elevation_options.keys()))
elevation_range = elevation_options[elevation_choice]

st.write(f"You selected an elevation change between {elevation_range[0]} and {elevation_range[1]} meters.")

# validate address function

# call address validation function here

# generate routes function using generate routes button
if st.button("Generate routes"):
    # do stuff
    ...