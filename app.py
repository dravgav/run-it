import openrouteservice.directions
import streamlit as st
import openrouteservice
from openrouteservice.directions import directions
import pandas as pd
import random
import folium
from streamlit_folium import st_folium
import polyline

# flag to save map onto screen
if "show_map" not in st.session_state:
    st.session_state["show_map"] = False

# openrouteservice api key initialization
ORS_API_KEY = st.secrets["openrouteservice"]["api_key"]
client = openrouteservice.Client(key=ORS_API_KEY)

# streamlit UI
st.title("Running Route Generator")

location = st.text_input("Enter your location address: ")

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
            return long, lat
        else:
            st.error("No location found given address, please enter a valid address")
            return None, None
    except Exception as error:
        st.error(f"An error has occurred while validating: {error}")
        return None, None


def generate_route(lat, long, dist_m, seed):
    """
    Given the origin (latitude and longitude) of the given address, random seed, and the preferred distance,
    generates a round-trip route using the number of points to create a loop route.
    Calls ORS to generate route/give directions based on these values. 
    Return GeoJSON route object, None if failed.
    """
    origin = [long, lat]
    coords = [origin]

    print(dist_m)

    try:
        route = openrouteservice.directions.directions(
            client, 
            coords, 
            profile="foot-walking", 
            units="km",
            options = {
                "round_trip": {
                    "length": dist_m,
                    "points": 3,
                    "seed": seed
            }
        })
        return route
    except Exception as e:
        st.error(f"Error generating route: {e}")
        return None



#  generate routes button process
if st.button("Generate routes", disabled=not filled): 
    if location:
        with st.spinner('Geocoding your location...'):
            long, lat = validate_address(location)
            if lat and long:
                st.success("Address has been successfully validated and geocoded")
                print(long, lat)
                
                # generate routes
                routes = []
                for i in range(3):
                    random_seed = random.randint(1, 1000)
                    route = generate_route(lat, long, distance_meters, random_seed)
                    routes.append(route)

                # update st flags
                st.session_state["show_map"] = True
                st.session_state["routes"] = routes

            else:
                st.error("Unable to validate and geocode location provided")
    else:
        st.warning("Please enter your current location")


# Displaying the running routes
if st.session_state["show_map"] and st.session_state["routes"]:
    st.title("Running Routes Below:")

    # create indices for each running route
    route_indices = list(range(len(st.session_state["routes"])))
    selected_route_idx = st.radio(
        "Select a route to display:",
        route_indices,
        format_func=lambda x: f"Route {x+1}"
    )
    
    # Get the selected route's encoded geometry
    selected_route = st.session_state["routes"][selected_route_idx]
    encoded_polyline = selected_route["routes"][0]["geometry"]
    
    # Decode polyline (running route) => get the list of (lat, lon)'s
    coords = polyline.decode(encoded_polyline)
    
    # Center map on the user's location
    m = folium.Map(location=coords[0], zoom_start=14)
    
    # Add running route
    folium.PolyLine(coords, color="blue", weight=3, tooltip=f"Route {selected_route_idx + 1}").add_to(m)
    
    # Add marker on user's location
    folium.Marker(
        location=coords[0],
        tooltip=f"Your Location!",
        icon=folium.Icon(color="red", icon="map-marker")
    ).add_to(m)
    
    # Display map
    st_folium(m, width=700, height=400)
