# Section 930 In-Class Exercise
# Mapping Napa Valley Wineries with Python and Mapbox
### DCDA Capstone Course — In-Class Exercise

---

## Overview

In this exercise you will use Python, Mapbox, and Folium to build an interactive web map of Napa Valley wineries. By the end of class you will have two maps saved as HTML files — one with a plain basemap and one with a custom "vineyard at sunset" style you design yourself. These skills map directly onto Lab 6.

You will complete five steps in order:

| Step | What You Do |
|------|-------------|
| 1 | Create a free Mapbox account |
| 2 | Run Script 1 — scrape winery data from the web |
| 3 | Run Script 2 — geocode addresses and build a basic map |
| 4 | Design your custom "vineyard at sunset" Mapbox style |
| 5 | Run Script 3 — rebuild the map with your custom style |

---

## Before You Begin

Make sure you have completed the environment setup:

1. Open VS Code and open the `930` folder as your workspace
2. Open a **Terminal** in VS Code: go to **Terminal → New Terminal**
3. Install the required Python libraries by running:

```
pip install -r requirements.txt
```

Wait for the installation to finish before proceeding.

---

## Step 1: Create Your Mapbox Account

Mapbox is a mapping platform that provides geocoding APIs, satellite imagery, and a style editor for designing custom maps. You will use it throughout this course.

**Instructions:**

1. Open a web browser and go to [https://mapbox.com](https://mapbox.com)
2. Click **Sign Up** (top right corner)
3. Fill in your name, email address, and a password
   - Use your school email address if possible
4. Check your email for a verification message from Mapbox and click the confirmation link
5. When prompted to choose a plan, select the **Free** plan (no credit card required)
6. Once inside your dashboard, take a moment to look around — you will see options for **Studio**, **Tokens**, and **Data**

> **Why are we doing this?**
> Mapbox provides two things we need: (1) a geocoding API that converts street addresses into latitude/longitude coordinates, and (2) a map style editor where we will design our custom basemap in Step 4.

---

## Step 2: Run Script 1 — Scrape Winery Data

In this step, Python will visit the Fort Ross Conservancy website, read the list of Napa Valley wineries, and save everything to a spreadsheet (CSV file).

**What is web scraping?**
Web scraping means writing code that automatically reads a webpage and pulls out specific data — like having a robot read the page and type everything into a spreadsheet for you. We use the `requests` library to download the page and `BeautifulSoup` to navigate the HTML.

**Instructions:**

1. In the VS Code terminal, make sure you are in the `930` folder:
   ```
   cd 930
   ```
   *(If you opened the `930` folder directly, you are already there.)*

2. Run Script 1:
   ```
   python scripts/01_scrape_napa_wineries.py
   ```

3. Watch the terminal output — you should see the script download the page, parse it, and report how many wineries it found.

4. When the script finishes, open the `data` folder in VS Code and click on `napa_wineries.csv` to explore it. You should see columns for **Name**, **Phone**, **Full_Address**, **City**, **State**, and **ZIP**.

**If you see an error:**
- `ConnectionError` — check your internet connection
- `ModuleNotFoundError` — you may not have run `pip install -r requirements.txt` yet
- The script says "0 wineries found" — the website may be temporarily down; let your instructor know

> **Note:** Some entries will have PO Box addresses or just a city name instead of a full street address. That is real-world data — not everything on a webpage is complete or consistent. Script 2 is designed to handle this gracefully.

---

## Step 3: Run Script 2 — Geocode Addresses and Build a Basic Map

Script 2 does two things: (1) it turns addresses into GPS coordinates using the Mapbox API, and (2) it builds an interactive map with those coordinates.

### Part A: Get Your Mapbox Access Token

To use the Mapbox Geocoding API, your Python script needs to authenticate with Mapbox using an **access token** — think of it like a password that tells Mapbox "this request is from a real authorized user."

**How to find your token:**

1. Go to [https://account.mapbox.com/access-tokens/](https://account.mapbox.com/access-tokens/)
2. Sign in to your Mapbox account
3. You will see a token labeled **"Default public token"** that starts with `pk.`
4. Click the **copy** icon next to it

> **Important:** Your token is personal. Do not share it publicly or post it in a GitHub repository. For this class exercise, pasting it directly in the script is fine. In professional settings, tokens are stored in environment variables, not in code files.

### Part B: Add Your Token to the Script

1. In VS Code, open `scripts/02_geocode_map_basic.py`
2. Find this line near the top of the file:
   ```python
   MAPBOX_TOKEN = "PASTE_YOUR_MAPBOX_TOKEN_HERE"
   ```
3. Replace `PASTE_YOUR_MAPBOX_TOKEN_HERE` with your actual token (keep the quotation marks):
   ```python
   MAPBOX_TOKEN = "pk.eyJ1IjoieW91cnVzZXJuYW1lIiwiYSI6ImNsZX..."
   ```
4. Save the file (**Ctrl+S**)

### Part C: Run the Script

In the terminal, run:
```
python scripts/02_geocode_map_basic.py
```

The script will:
- Loop through every winery address
- Send each one to Mapbox and receive coordinates back
- Save a new CSV with `Latitude` and `Longitude` columns added
- Create an interactive map and save it as `data/napa_wineries_map_basic.html`

**To view your map:**
1. In VS Code's Explorer panel (left side), expand `930 → data`
2. Right-click `napa_wineries_map_basic.html`
3. Select **Open with Live Server** if you have the Live Server extension, **or** right-click the file in File Explorer and open it with your browser

You should see a map of Napa Valley with red dots for each winery. Click any dot to see its popup with the name, address, and phone number.

> **Why does the script pause between requests?** Sending thousands of requests to an API all at once can get your account flagged or rate-limited. We add a 0.1 second pause between each call — this is called "rate limiting" your own requests, and it's considered good practice.

---

## Step 4: Design Your Custom Mapbox Style — "Vineyard at Sunset"

In this step you will create a custom map style in Mapbox Studio that evokes the warm, atmospheric feeling of a Napa Valley vineyard at golden hour. Your canvas will have the soft golds, deep burgundies, and hazy purples of a wine country sunset.

### Suggested Color Palette

| Element | Color | Hex Code | Notes |
|---------|-------|----------|-------|
| Land (base) | Warm parchment | `#F5E5C8` | Like dry grass in late afternoon sun |
| Water (bays, rivers) | Twilight steel blue | `#7A9EB5` | Cool contrast to warm land |
| Ocean / large water bodies | Deep twilight blue | `#4A7A9B` | Deepens the sunset mood |
| Major roads | Terracotta / brick | `#C87040` | Warm, earthy road color |
| Minor roads / streets | Light tan | `#D4B896` | Subtle, doesn't compete with POIs |
| Motorways / highways | Burnt sienna | `#B85C2A` | Bold enough to navigate |
| Land use (parks, forests) | Dusty sage | `#A8B87A` | Vineyard green, slightly muted |
| Urban areas | Sandy rose | `#DDC8B0` | Slightly warmer than base land |
| Labels (place names) | Deep burgundy | `#5C1A2A` | Wine-colored text |
| Sky | Sunset gradient | `#D4856A` → `#9B4E7A` | Coral fading to violet |

### Step-by-Step Instructions

**Create a New Style:**

1. Go to [https://studio.mapbox.com](https://studio.mapbox.com) and sign in
2. On your Studio dashboard, click the **"+ New style"** button
3. When asked to choose a template, scroll to find and select **"Blank"** — this starts you from a completely empty canvas with no pre-made colors or layers
4. Click **"Customize Blank"**
5. The Mapbox Studio style editor will open. You will see a dark empty canvas — that is your map, waiting to be styled

**Add and Style the Land Component:**

6. In the left panel, click **"+ Add component"**
7. Select **"Land, water, & sky"**
8. The component will be added to your panel. Click on it to expand its settings.
9. Set the **Land color** to `#F5E5C8`
10. Set the **Water color** to `#7A9EB5`
11. Set the **Ocean color** to `#4A7A9B`
12. If a **Sky color** option is available, set it to `#D4856A` (sunset coral)

**Add and Style the Road Network:**

13. Click **"+ Add component"** again and select **"Road network"**
14. Expand the road settings and customize each road type:
    - **Motorway** (freeway): color `#B85C2A`, width slightly thicker
    - **Primary road**: color `#C87040`
    - **Secondary/local roads**: color `#D4B896`
15. Toggle road labels **ON** — styled in deep burgundy `#5C1A2A`

**Add Place Labels:**

16. Click **"+ Add component"** → select **"Place labels"**
17. Change the label color to `#5C1A2A` (deep burgundy)
18. Choose a font that fits the aesthetic — try **"Merriweather"** or **"EB Garamond"** for a classic wine-country feeling if available, or use **"Source Serif Pro"**
19. Make city names slightly larger, neighborhood names smaller

**Add Land Use (Parks and Green Spaces):**

20. Click **"+ Add component"** → select **"Land use"** or look for **"Parks & recreation"**
21. Set park/forest fill color to `#A8B87A` (dusty sage green)

**Add POI Labels (Points of Interest):**

22. Click **"+ Add component"** → select **"POI labels"**
23. Set POI icon/label color matching the theme — try `#7A4A60` (muted mauve)

**Style Across Zoom Levels:**

24. Click on any layer in your style panel
25. Look for **"Style across zoom range"** option — this lets you change how a layer looks at different zoom levels
26. For road widths: make roads thicker at higher zoom (zoomed in) and thinner or invisible at lower zoom (zoomed out)
27. For labels: make labels appear only above zoom level 8 or 9 to avoid clutter at small scales
28. Test your map at different zoom levels using the zoom controls on the map canvas

**Publish Your Style:**

29. When you are satisfied with your design, click the **"Publish"** button in the top right corner of Mapbox Studio
30. A dialog will appear — click **"Publish"** to confirm
31. Your style is now live and can be accessed via the API

**Get Your Style URL:**

32. Click the **"Share"** button (near the Publish button)
33. In the share dialog, look for **Visibility** and set it to **"Public"**
34. Find your **Style URL** — it looks like:
    ```
    mapbox://styles/yourusername/clxabcdefghij1234567890
    ```
35. Copy this URL and keep it somewhere handy — you will need it for Script 3

---

## Step 5: Run Script 3 — Map with Your Custom Style

Now you will rebuild the map using your custom "vineyard at sunset" Mapbox style as the basemap.

### Part A: Add Your Credentials to Script 3

1. Open `scripts/03_map_custom_style.py` in VS Code
2. Find and fill in both variables near the top:

```python
# Your Mapbox public token (starts with "pk.")
MAPBOX_TOKEN = "pk.eyJ1IjoieW91cnVzZXJuYW1l..."

# Your Style URL from Mapbox Studio
MAPBOX_STYLE_URL = "mapbox://styles/yourusername/yourstyleid"
```

3. Save the file (**Ctrl+S**)

### Part B: Run the Script

```
python scripts/03_map_custom_style.py
```

The script will create `data/napa_wineries_map_custom.html`.

Open it in your browser and compare it to your Script 2 result:

- `data/napa_wineries_map_basic.html` — plain OpenStreetMap
- `data/napa_wineries_map_custom.html` — your vineyard-at-sunset custom style

Congratulations — you now have a fully styled interactive web map ready for your portfolio!

---

## Connection to Lab 6

Everything you did today is directly used in Lab 6:

| Today's Exercise | Lab 6 Equivalent |
|-----------------|------------------|
| Script 1 — web scraping | You will create your own locations CSV manually |
| Script 2 — Mapbox geocoding | Exact same API call, on your own dataset |
| Script 2 — Folium with OpenStreetMap | Same code structure for your Lab 6 map |
| Step 4 — Mapbox Studio style | Lab 6 Part 1 — you design your own inspired style |
| Script 3 — custom tile URL | Lab 6 Part 3 Step 4 — connecting your style to Python |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'requests'` | Run `pip install -r requirements.txt` again |
| `KeyError` when running Script 2 | Check that Script 1 ran successfully and `data/napa_wineries.csv` exists |
| Map opens but shows a blank grey canvas | Your Mapbox token is wrong or your style is set to Private — double-check both |
| Map shows OSM instead of your custom style | Make sure you pasted the correct Style URL, not the tile URL |
| Geocoding returns None for many addresses | PO Boxes and city-only addresses cannot be geocoded — this is expected |
