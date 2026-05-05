import pandas as pd
import requests
import folium
from urllib.parse import quote
import os

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(WORKSPACE_DIR, "930", "data", "hometown_map_fixed.html")
OUTPUT_DIR = os.path.dirname(OUTPUT_PATH)


def relative_image_path(filename):
    return os.path.relpath(os.path.join(WORKSPACE_DIR, "images", filename), OUTPUT_DIR).replace("\\", "/")

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

# Actual New Jersey location images - saved locally for reliable display
local_images = {
    "Liberty State Park":       relative_image_path("liberty_state_park.jpg"),
    "Liberty Science Center":   relative_image_path("liberty_science_center.jpg"),
    "Princeton University":     relative_image_path("princeton_university.jpg"),
    "Six Flags Great Adventure": relative_image_path("six_flags.jpg"),
    "Point Pleasant Beach":     relative_image_path("point_pleasant.jpg"),
    "Grounds for Sculpture":    relative_image_path("grounds_for_sculpture.jpg"),
    "Branch Brook Park":        relative_image_path("branch_brook_park.jpg"),
    "American Dream Mall":      relative_image_path("american_dream_mall.jpg"),
    "The Stone Pony":           relative_image_path("stone_pony.jpg"),
    "Asbury Park Boardwalk":    relative_image_path("asbury_park.jpg"),
}

# Add markers
for i, row in df.iterrows():
    color = color_map.get(row["Type"], "gray")
    
    # Use local image URL for better reliability
    image_url = local_images.get(row["Name"], "https://via.placeholder.com/300x200?text=No+Image")

    popup_html = f"""
    <div style="max-width: 320px; font-family: Arial, sans-serif;">
        <h3 style="color: #2c3e50; margin: 0 0 12px 0; font-size: 18px; font-weight: bold;">{row['Name']}</h3>
        <p style="margin: 0 0 15px 0; font-size: 14px; line-height: 1.5; color: #34495e;">{row['Description']}</p>
        <div style="position: relative; margin-bottom: 12px;">
            <img src="{image_url}" 
                 style="width: 100%; max-width: 300px; height: 200px; object-fit: cover; border-radius: 10px; border: 3px solid #3498db; box-shadow: 0 4px 8px rgba(0,0,0,0.1);" 
                 onerror="this.src='https://via.placeholder.com/300x200/e74c3c/ffffff?text=Actual+Location+Photo'; this.style.opacity='0.8';"
                 alt="Photo of {row['Name']}"
                  title="Click to see {row['Name']}">
            <div style="position: absolute; bottom: 8px; right: 8px; background: rgba(0,0,0,0.7); color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px;">
                📸 Real Photo
            </div>
        </div>
        <div style="background: #ecf0f1; padding: 8px 12px; border-radius: 6px; border-left: 4px solid #3498db;">
            <div style="font-size: 12px; color: #7f8c8d; margin-bottom: 4px;">📍 <strong>Address:</strong></div>
            <div style="font-size: 13px; color: #2c3e50;">{row['Address'] if pd.notna(row['Address']) else 'Located in New Jersey'}</div>
        </div>
        <div style="margin-top: 10px; font-size: 11px; color: #95a5a6; text-align: center; font-style: italic;">
            Visit this authentic New Jersey location and experience it yourself!
        </div>
    </div>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=350),
        icon=folium.Icon(color=color, icon="info-sign")
    ).add_to(m)

# Save map
m.save(OUTPUT_PATH)

print(f"Fixed map created successfully: {OUTPUT_PATH}")
print("\nTo view with images:")
print("1. Open 930/data/hometown_map_fixed.html in preview or your browser")
print("2. The popup images load from the workspace images folder automatically")