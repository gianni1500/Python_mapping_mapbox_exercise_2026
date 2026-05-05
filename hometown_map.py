import pandas as pd
import requests
import folium
from urllib.parse import quote

# YOUR MAPBOX TOKEN
access_token = "pk.eyJ1IjoiZ2lhbm5pODAwIiwiYSI6ImNtbHRvZGloZDAyZXAzZG9yeDU4NWhuZHYifQ.zgTV_NQ7QPVeommiLkqGaw"

# YOUR CUSTOM MAPBOX STYLE
tiles = "https://api.mapbox.com/styles/v1/gianni800/cmmclvong00cg01ry1haohbaw/tiles/256/{z}/{x}/{y}@2x?access_token=" + access_token

# Load CSV
df = pd.read_csv("hometown_locations.csv")

# Function to geocode address using Mapbox
def geocode(address):

    encoded = quote(address)

    url = f"https://api.mapbox.com/search/geocode/v6/forward?q={encoded}&access_token={access_token}"

    response = requests.get(url).json()

    if response["features"]:
        coords = response["features"][0]["geometry"]["coordinates"]
        return coords[1], coords[0]
    else:
        return None, None


# Geocode addresses
latitudes = []
longitudes = []

for address in df["Address"]:
    lat, lon = geocode(address)
    latitudes.append(lat)
    longitudes.append(lon)

df["lat"] = latitudes
df["lon"] = longitudes


# Create base map centered on NJ
m = folium.Map(
    location=[40.2, -74.5],
    zoom_start=8,
    tiles=tiles,
    attr="Mapbox"
)

# Marker colors by type
color_map = {
    "Restaurant": "red",
    "Park": "green",
    "School": "blue",
    "Cultural": "purple",
    "Historical": "orange",
    "Recreation": "cadetblue",
    "Shopping": "pink"
}

# Add markers
for i, row in df.iterrows():

    color = color_map.get(row["Type"], "gray")

    popup_html = f"""
    <div style="max-width: 300px;">
        <h3 style="color: #333; margin-bottom: 10px;">{row['Name']}</h3>
        <p style="margin-bottom: 15px;">{row['Description']}</p>
        <img src="{row['Image_URL']}" width="280" style="border-radius: 5px; display: block;" 
             onerror="this.src='https://via.placeholder.com/280x200?text=Image+Not+Available'; this.style.opacity='0.5';" 
             loading="lazy" crossorigin="anonymous">
    </div>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=300),
        icon=folium.Icon(color=color, icon="info-sign")
    ).add_to(m)

# Save map
m.save("hometown_map.html")

print("Map created successfully: hometown_map.html")