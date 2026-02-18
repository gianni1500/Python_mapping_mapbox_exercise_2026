# =============================================================================
# SCRIPT 2 — Section 200: Geocode TX Hill Country Wineries & Create Basic Map
# =============================================================================
# WHAT THIS SCRIPT DOES:
#   1. Reads the winery CSV from Script 1
#   2. Geocodes each address using the Mapbox Geocoding API
#   3. Saves the data with lat/lon coordinates as a new CSV
#   4. Creates an interactive Folium map using a basic OpenStreetMap basemap
#   5. Saves the map as an HTML file
#
# BEFORE YOU RUN:
#   - Add your Mapbox access token below
#   - Make sure Script 1 ran successfully (data/tx_hill_wineries.csv must exist)
#
# OUTPUT:
#   data/tx_hill_wineries_geocoded.csv
#   data/tx_hill_wineries_map_basic.html
#
# TO RUN:
#   python scripts/02_geocode_map_basic.py
# =============================================================================


# =============================================================================
# STEP 1: IMPORT LIBRARIES
# =============================================================================

import requests
import pandas as pd
import folium
import os
import time


# =============================================================================
# STEP 2: ADD YOUR MAPBOX ACCESS TOKEN
# =============================================================================
# Token starts with "pk." — find it at: https://account.mapbox.com/access-tokens/

MAPBOX_TOKEN = "PASTE_YOUR_MAPBOX_TOKEN_HERE"

if MAPBOX_TOKEN == "PASTE_YOUR_MAPBOX_TOKEN_HERE":
    print("ERROR: Please add your Mapbox access token to MAPBOX_TOKEN.")
    print("  Get it at: https://account.mapbox.com/access-tokens/")
    exit()


# =============================================================================
# STEP 3: DEFINE THE GEOCODING FUNCTION
# =============================================================================

def geocode_address(address_string, token):
    """
    Send a text address to the Mapbox Geocoding API and return (lat, lon).

    The Mapbox API v6 'forward geocoding' endpoint accepts a text address
    and returns a GeoJSON FeatureCollection. We extract the coordinates
    from the first (best) result.

    Parameters:
        address_string (str): Full address as text
        token (str): Mapbox public access token

    Returns:
        tuple: (latitude, longitude) as floats, or (None, None) if not found
    """

    if not address_string or len(address_string.strip()) < 5:
        return None, None

    # Build the request URL.
    # requests.utils.quote() URL-encodes special characters in the address.
    # Without this, spaces and commas in the address would break the URL.
    url = (
        f"https://api.mapbox.com/search/geocode/v6/forward"
        f"?q={requests.utils.quote(address_string)}"
        f"&country=us"     # US addresses only — improves accuracy
        f"&limit=1"        # Only return the best single match
        f"&access_token={token}"
    )

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None, None

        # Parse the JSON response
        data = resp.json()
        features = data.get("features", [])

        if features:
            # GeoJSON coordinates are [longitude, latitude] — reversed from what
            # you might expect! We swap them: coords[1] = lat, coords[0] = lon
            coords = features[0]["geometry"]["coordinates"]
            return coords[1], coords[0]  # Return (latitude, longitude)

    except requests.exceptions.RequestException:
        return None, None

    return None, None


# =============================================================================
# STEP 4: LOAD THE WINERY DATA
# =============================================================================
print("=" * 60)
print("  TX Hill Country Wineries — Geocoder & Basic Map Builder")
print("=" * 60)

input_path = os.path.join("data", "tx_hill_wineries.csv")

if not os.path.exists(input_path):
    print(f"\nERROR: Cannot find {input_path}")
    print("Please run Script 1 first: 01_scrape_tx_hill_wineries.py")
    exit()

df = pd.read_csv(input_path)
print(f"\nLoaded {len(df)} wineries from: {input_path}")


# =============================================================================
# STEP 5: GEOCODE ADDRESSES
# =============================================================================
print("\nGeocoding winery addresses via Mapbox API...")
print("(Takes a minute — we pause briefly between each call.)")

latitudes = []
longitudes = []

for i, row in df.iterrows():
    # Use the Full_Address field (most complete, combining street + city + state + zip)
    address = row.get("Full_Address", "")
    full_name = row.get("Name", f"Row {i}")

    print(f"  [{i+1}/{len(df)}] {full_name[:45]}...")

    lat, lon = geocode_address(address, MAPBOX_TOKEN)
    latitudes.append(lat)
    longitudes.append(lon)

    # 0.1 second pause between API requests
    time.sleep(0.1)

df["Latitude"] = latitudes
df["Longitude"] = longitudes

success_count = df["Latitude"].notna().sum()
print(f"\nGeocode results: {success_count} succeeded, {len(df) - success_count} failed")


# =============================================================================
# STEP 6: SAVE GEOCODED CSV
# =============================================================================
os.makedirs("data", exist_ok=True)
geocoded_path = os.path.join("data", "tx_hill_wineries_geocoded.csv")
df.to_csv(geocoded_path, index=False, encoding="utf-8-sig")
print(f"Saved geocoded data to: {geocoded_path}")


# =============================================================================
# STEP 7: BUILD THE FOLIUM MAP
# =============================================================================
print("\nBuilding interactive map...")

df_mapped = df.dropna(subset=["Latitude", "Longitude"]).copy()
print(f"  Mapping {len(df_mapped)} wineries with valid coordinates.")

# Center the map on the heart of the Texas Hill Country
# (Fredericksburg, TX is roughly the geographic center of the wine trail)
if len(df_mapped) > 0:
    center_lat = df_mapped["Latitude"].mean()
    center_lon = df_mapped["Longitude"].mean()
else:
    center_lat = 30.2752  # Fredericksburg, TX
    center_lon = -98.8720

tx_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles="OpenStreetMap"
)

# --- Title ---
title_html = """
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
     z-index: 1000; background-color: white; padding: 10px 20px;
     border: 2px solid #BF5700; border-radius: 8px; font-family: Georgia, serif;
     font-size: 16px; font-weight: bold; color: #BF5700;
     box-shadow: 2px 2px 6px rgba(0,0,0,0.3);">
    🍷 Texas Hill Country Wineries
</div>
"""
tx_map.get_root().html.add_child(folium.Element(title_html))

# --- Add Winery Markers ---
for i, row in df_mapped.iterrows():

    # Build popup content including extra details available from the scraper
    hours = row.get("Hours", "")
    desc = row.get("Description", "")
    city = row.get("City", "")
    website = row.get("Website", "")

    hours_html = f"<b>⏰ Hours:</b> {hours}<br>" if hours else ""
    desc_html = f"<br><span style='font-size: 12px;'>{desc[:250]}...</span>" if desc else ""
    website_html = (
        f"<br><a href='{website}' target='_blank' style='color: #BF5700;'>Visit Website ↗</a>"
        if website else ""
    )

    popup_html = f"""
    <div style="font-family: Arial, sans-serif; font-size: 13px;
                min-width: 220px; max-width: 320px;">
        <h4 style="margin: 0 0 6px 0; color: #BF5700;
                   border-bottom: 1px solid #ccc; padding-bottom: 4px;">
            {row['Name']}
        </h4>
        <b>📍 {row.get('Full_Address', city)}</b><br>
        {hours_html}
        {desc_html}
        {website_html}
    </div>
    """

    # Use orange/tan-toned circle markers to evoke Texas Hill Country aesthetics
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=7,
        color="#BF5700",       # UT burnt orange border (also a warm Hill Country tone)
        fill=True,
        fill_color="#D87035",  # Slightly lighter orange fill
        fill_opacity=0.75,
        popup=folium.Popup(popup_html, max_width=340),
        tooltip=f"🍷 {row['Name']} — {city}"
    ).add_to(tx_map)

folium.LayerControl().add_to(tx_map)


# =============================================================================
# STEP 8: SAVE THE MAP
# =============================================================================
map_output_path = os.path.join("data", "tx_hill_wineries_map_basic.html")
tx_map.save(map_output_path)

print(f"  Map saved to: {map_output_path}")
print("\n" + "=" * 60)
print("  SCRIPT COMPLETE!")
print("=" * 60)
print(f"\nOpen your map: {map_output_path}")
print("\nNow follow Step 4 in the instructions to build your UT-themed")
print("custom Mapbox style, then run Script 3!")
