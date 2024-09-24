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
    min_dist, max_dist = 1.0, 48.0
    step = 0.5
if unit == "mi":
    min_dist, max_dist = 1.0, 30.0
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

filled = bool(location and elevation_choice and distance)

# validate address by converting into latitude,longitude coordinates for generating routes
# TODO: geocoding done, figure out better validation
def validate_address(address):
    try: 
        print(address)
        geoCode = client.pelias_search(text=address)

        if geoCode['features']:
            coords = geoCode['features'][0]['geometry']['coordinates']
            long, lat = coords
            return lat, long
        else:
            st.error("No location found given address, please enter a valid address")
            return None, None
    except Exception as error:
        st.error(f"An error has occurred while validating: {error}")
        return None, None

# TODO: generate routes function

#  generate routes button process
if st.button("Generate routes", disabled=not filled): 
    if location:
        with st.spinner('Geocoding your location...'):
            lat, long = validate_address(location)
            if lat and long:
                st.success("Address has been successfully validated and geocoded")
                print(lat, long)
                # TODO: get routes
            else:
                st.error("Unable to validate and geocode location provided")
    else:
        st.warning("Please enter your current location")