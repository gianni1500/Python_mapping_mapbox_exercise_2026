# =============================================================================
# SCRIPT 3 — Section 200: Create Map with Custom UT-Themed Mapbox Style
# =============================================================================
# WHAT THIS SCRIPT DOES:
#   Recreates the Texas Hill Country winery map using your custom Mapbox
#   basemap style — designed in the University of Texas at Austin color palette
#   (burnt orange, white, warm grey, limestone tan, dark charcoal).
#
# BEFORE YOU RUN:
#   1. Complete Step 4 in the instructions (build your custom UT-themed style)
#   2. Publish the style and copy your Style URL from Mapbox Studio
#   3. Fill in MAPBOX_TOKEN and MAPBOX_STYLE_URL below
#   4. Script 2 must have already been run (data/tx_hill_wineries_geocoded.csv)
#
# OUTPUT:
#   data/tx_hill_wineries_map_custom.html
#
# TO RUN:
#   python scripts/03_map_custom_style.py
# =============================================================================


# =============================================================================
# STEP 1: IMPORT LIBRARIES
# =============================================================================

import pandas as pd
import folium
import os


# =============================================================================
# STEP 2: ADD YOUR MAPBOX CREDENTIALS
# =============================================================================

# --- A) Mapbox Access Token ---
# Starts with "pk." — find it at: https://account.mapbox.com/access-tokens/
MAPBOX_TOKEN = "PASTE_YOUR_MAPBOX_TOKEN_HERE"

# --- B) Mapbox Style URL ---
# HOW TO FIND IT:
#   1. Open https://studio.mapbox.com
#   2. Click your custom style
#   3. Click "Share" (top right) → set to "Public"
#   4. Copy the URL: mapbox://styles/yourusername/yourstyleid
MAPBOX_STYLE_URL = "mapbox://styles/YOUR_USERNAME/YOUR_STYLE_ID"

# --- Validation ---
if MAPBOX_TOKEN == "PASTE_YOUR_MAPBOX_TOKEN_HERE":
    print("ERROR: Add your Mapbox access token to the MAPBOX_TOKEN variable.")
    exit()

if "YOUR_USERNAME" in MAPBOX_STYLE_URL or "YOUR_STYLE_ID" in MAPBOX_STYLE_URL:
    print("ERROR: Add your Mapbox Style URL to the MAPBOX_STYLE_URL variable.")
    print("  Format: mapbox://styles/yourusername/yourstyleid")
    exit()


# =============================================================================
# STEP 3: CONVERT STYLE URL TO TILE URL
# =============================================================================
# Mapbox style URLs are identifiers, not HTTP addresses.
# Folium needs an actual HTTP "tile URL" to load map imagery from the web.
# We convert using the Mapbox Styles API tile URL pattern.
#
# From: mapbox://styles/username/styleid
# To:   https://api.mapbox.com/styles/v1/username/styleid/tiles/256/{z}/{x}/{y}@2x?access_token=...
#
# {z}, {x}, {y} are NOT Python format strings — they are Leaflet/Folium
# placeholders that get filled in automatically as the user pans and zooms.
# We use {{z}}, {{x}}, {{y}} in the Python f-string to produce literal {z}, {x}, {y}.

style_path = MAPBOX_STYLE_URL.replace("mapbox://styles/", "")

TILE_URL = (
    f"https://api.mapbox.com/styles/v1/{style_path}/tiles/256/{{z}}/{{x}}/{{y}}@2x"
    f"?access_token={MAPBOX_TOKEN}"
)

TILE_ATTRIBUTION = (
    '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> '
    '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
)

print("=" * 60)
print("  TX Hill Country Wineries — Custom UT-Themed Mapbox Style Map")
print("=" * 60)
print(f"\nUsing custom style: {MAPBOX_STYLE_URL}")


# =============================================================================
# STEP 4: LOAD GEOCODED DATA
# =============================================================================
input_path = os.path.join("data", "tx_hill_wineries_geocoded.csv")

if not os.path.exists(input_path):
    print(f"\nERROR: File not found: {input_path}")
    print("Please run Script 2 first: 02_geocode_map_basic.py")
    exit()

df = pd.read_csv(input_path)
df_mapped = df.dropna(subset=["Latitude", "Longitude"]).copy()

print(f"\nLoaded {len(df)} wineries. {len(df_mapped)} have coordinates for mapping.")


# =============================================================================
# STEP 5: BUILD THE MAP WITH CUSTOM BASEMAP
# =============================================================================
print("\nBuilding map with custom Mapbox basemap...")

center_lat = df_mapped["Latitude"].mean() if len(df_mapped) > 0 else 30.2752
center_lon = df_mapped["Longitude"].mean() if len(df_mapped) > 0 else -98.8720

# Create the Folium map — this time using our custom Mapbox tile layer
tx_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,
    tiles=TILE_URL,
    attr=TILE_ATTRIBUTION
)

# --- Title (styled with UT burnt orange) ---
title_html = """
<div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
     z-index: 1000; background-color: rgba(191, 87, 0, 0.92); padding: 10px 20px;
     border: 2px solid white; border-radius: 8px; font-family: Georgia, serif;
     font-size: 16px; font-weight: bold; color: white;
     box-shadow: 2px 2px 6px rgba(0,0,0,0.5);">
    🍷 Texas Hill Country Wineries
</div>
"""
tx_map.get_root().html.add_child(folium.Element(title_html))

# --- Add Winery Markers ---
for i, row in df_mapped.iterrows():
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

    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=7,
        color="#BF5700",
        fill=True,
        fill_color="#D87035",
        fill_opacity=0.75,
        popup=folium.Popup(popup_html, max_width=340),
        tooltip=f"🍷 {row['Name']} — {city}"
    ).add_to(tx_map)

folium.LayerControl().add_to(tx_map)


# =============================================================================
# STEP 6: SAVE THE MAP
# =============================================================================
os.makedirs("data", exist_ok=True)
output_path = os.path.join("data", "tx_hill_wineries_map_custom.html")
tx_map.save(output_path)

print(f"  Map saved to: {output_path}")
print("\n" + "=" * 60)
print("  SCRIPT COMPLETE!")
print("=" * 60)
print(f"\nCompare your two maps:")
print(f"  data/tx_hill_wineries_map_basic.html   ← plain OpenStreetMap")
print(f"  data/tx_hill_wineries_map_custom.html  ← YOUR custom UT-themed style")
print(f"\nThis file is portfolio-ready!")
