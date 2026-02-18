# Section 200 In-Class Exercise
# Mapping the Texas Hill Country Wine Trail with Python and Mapbox
### DCDA Capstone Course — In-Class Exercise

---

## Overview

In this exercise you will scrape a real member-winery listing from the Texas Hill Country Wineries organization, geocode the addresses, and build two versions of an interactive web map — one using a plain basemap and one using a custom UT Austin-themed style you design in Mapbox Studio. Because this site uses server-side HTML rendering (unlike the JavaScript-heavy Texas Monthly site covered in other sections), the scraper works fully end-to-end.

You will complete five steps:

| Step | What You Do |
|------|-------------|
| 1 | Create a free Mapbox account |
| 2 | Run Script 1 — scrape TX Hill Country Wineries member list |
| 3 | Run Script 2 — geocode addresses and build a basic map |
| 4 | Design your custom UT Austin-themed Mapbox style |
| 5 | Run Script 3 — rebuild the map with your custom style |

---

## Before You Begin

1. Open VS Code and open the `200` folder as your workspace
2. Open a **Terminal**: **Terminal → New Terminal**
3. Install required libraries:

```
pip install -r requirements.txt
```

Wait for it to finish.

---

## Step 1: Create Your Mapbox Account

**Instructions:**

1. Go to [https://mapbox.com](https://mapbox.com) and click **Sign Up**
2. Use your school email if possible; fill in name and password
3. Click the verification link in your email
4. Choose the **Free** plan — no credit card needed
5. Take note of the **Studio** and **Tokens** sections on your dashboard — you will use both today

> If you already have a Mapbox account from a previous exercise or lab, use the same account.

---

## Step 2: Run Script 1 — Scrape Texas Hill Country Wineries

In this step Python will visit [texashillcountrywineries.org](https://texashillcountrywineries.org/pages/winery-listing-page), extract every member winery's name, address, hours, website, and description, and save everything to a CSV file.

### What Makes This Scrape Possible?

The Texas Hill Country Wineries site is built on **Shopify** and renders its winery listing content as **server-side HTML** — meaning the full content (including winery names and addresses) is present in the raw HTML that Python downloads. This is the best-case scenario for scraping.

Contrast this with sites like Texas Monthly, which use client-side JavaScript to inject content after the page loads. Those require more advanced tools (Selenium or Playwright). This class section is lucky — your target site works cleanly with `requests` + `BeautifulSoup`!

### Understanding the HTML Structure

When Python downloads a webpage, it gets the raw HTML — the same code your browser uses to display the page. Here is a simplified example of what one winery entry looks like in the HTML:

```html
<div class="winery-card">
  <h3>Becker Vineyards</h3>
  <p>464 Becker Farms Rd<br>Fredericksburg, Texas 78624</p>
  <p>HOURS: Mon-Thur 10-5, Fri & Sat 10-6, Sun 11-6</p>
  <a href="http://beckervineyards.com/">Visit Website</a>
  <p>Featured in Wine Spectator, Food & Wine, Bon Appetit...</p>
</div>
```

`BeautifulSoup` lets us navigate this structure and extract the text inside specific tags. Script 1 finds each "Visit Website" link (every winery has one) and uses it as an anchor to locate the surrounding winery name, address, hours, and description.

**Run the Script:**

1. In the terminal, navigate to the `200` folder:
   ```
   cd 200
   ```
2. Run Script 1:
   ```
   python scripts/01_scrape_tx_hill_wineries.py
   ```
3. Watch the output — you should see it find 50+ winery entries

4. When done, explore `data/tx_hill_wineries.csv`. You should see columns for **Name**, **Street_Address**, **City**, **State**, **ZIP**, **Hours**, **Website**, and **Description**.

**Troubleshooting:**
- `ConnectionError` — check your internet connection
- `ModuleNotFoundError` — make sure you ran `pip install -r requirements.txt`
- Fewer than 20 wineries found — the website may have been updated since this exercise was written; let your instructor know

---

## Step 3: Run Script 2 — Geocode and Build a Basic Map

Script 2 converts each winery's address to GPS coordinates using the Mapbox Geocoding API and creates an interactive map with Folium.

### Part A: Get Your Mapbox Access Token

To use Mapbox APIs, your script needs an **access token** — a unique key that authenticates your requests. Think of it as your API "password."

**How to find it:**

1. Go to [https://account.mapbox.com/access-tokens/](https://account.mapbox.com/access-tokens/)
2. Sign in to Mapbox
3. Copy the **"Default public token"** — it starts with `pk.`

> **Security note:** Your access token is personal. Never commit it to GitHub or share it publicly. For this class we paste it directly in the script, which is fine for local exercises. In production, tokens live in environment variables (`.env` files).

### Part B: Add Token to Script 2

1. Open `scripts/02_geocode_map_basic.py`
2. Find this line:
   ```python
   MAPBOX_TOKEN = "PASTE_YOUR_MAPBOX_TOKEN_HERE"
   ```
3. Replace with your real token (keep the quotes):
   ```python
   MAPBOX_TOKEN = "pk.eyJ1IjoieW91cnVzZXJuYW1l..."
   ```
4. Save (**Ctrl+S**)

### Part C: Run the Script

```
python scripts/02_geocode_map_basic.py
```

**How the Mapbox Geocoding API works:**

When you run this script, for each winery it sends an HTTP request to a URL that looks like:

```
https://api.mapbox.com/search/geocode/v6/forward
    ?q=464 Becker Farms Rd, Fredericksburg, Texas 78624
    &country=us
    &limit=1
    &access_token=pk.eyJ1...
```

Mapbox looks up that address in its database and returns a JSON response:

```json
{
  "features": [{
    "geometry": {
      "coordinates": [-98.8714, 30.2821]
    }
  }]
}
```

The coordinates `[-98.8714, 30.2821]` are `[longitude, latitude]`. Note the order — in GeoJSON format, longitude always comes first, even though we usually say "latitude, longitude" in everyday speech. The script swaps them to the correct order for Folium.

**When Script 2 finishes:**
- `data/tx_hill_wineries_geocoded.csv` — CSV with Latitude and Longitude columns added
- `data/tx_hill_wineries_map_basic.html` — interactive map, open in browser

Open the map! You should see 50+ wineries plotted across the Texas Hill Country, clustered around Fredericksburg, Johnson City, and Stonewall. Click any marker for a popup showing the winery's name, address, hours, description, and a link to their website.

> **Why do some wineries fail to geocode?** Geocoding is not perfect. Addresses that are unusual (rural route roads, very new developments, or addresses outside Mapbox's database coverage) may return no results. This is normal — you will see a count of successes vs. failures in the terminal output.

---

## Step 4: Design Your Custom Mapbox Style — UT Austin Color Palette

In this step you will create a map style inspired by The University of Texas at Austin's visual identity. The palette centers on **burnt orange** (`#BF5700`) as the signature color, balanced with **warm grey**, **limestone tan** (nodding to Austin's geology), **white**, and **dark charcoal**.

### UT Austin Color Reference

| Map Element | Color Name | Hex Code | Notes |
|-------------|----------|----------|-------|
| Land (base) | Limestone tan | `#EDE0C8` | Warm, pale — evokes Texas Hill Country limestone |
| Water (rivers, lakes) | Muted steel blue | `#8FA8BE` | Cool contrast to warm land |
| Ocean / large water | Deep muted blue | `#5B8FA8` | Slightly deeper tone |
| Major roads (motorways) | Burnt orange | `#BF5700` | Signature UT color — use boldly on major roads |
| Primary roads | Warm terracotta | `#C87A50` | Lighter relative of burnt orange |
| Secondary / local roads | Warm grey | `#B0A090` | Subtle, doesn't compete |
| Parks / green spaces | Warm olive | `#9CAE85` | Texas Hill country vegetation tone |
| Urban areas | Light limestone | `#E0D4B8` | Slightly darker than base land |
| Place labels | Dark charcoal | `#333333` | Clean and readable |
| Road labels | White | `#FFFFFF` | Good contrast on darker road colors |
| POI labels | Burnt orange | `#BF5700` | Consistent with brand |

> **Design principle:** Burnt orange dominates the road hierarchy but stays out of the background. The map should feel warm and earthy — like looking at a topographic map of the Hill Country printed on cream paper, with orange ink for major routes.

### Step-by-Step Instructions

**Create a New Style:**

1. Go to [https://studio.mapbox.com](https://studio.mapbox.com)
2. Click **"+ New style"**
3. Select **"Blank"** template (critical — do not start from a pre-made style)
4. Click **"Customize Blank"**
5. The style editor opens with a dark empty canvas

**Add Land, Water, & Sky:**

6. Click **"+ Add component"** → **"Land, water, & sky"**
7. Set:
   - **Land**: `#EDE0C8` (limestone tan)
   - **Water**: `#8FA8BE` (muted steel blue)
   - **Ocean**: `#5B8FA8`

**Add the Road Network:**

8. Click **"+ Add component"** → **"Road network"**
9. Style each road tier:
   - **Motorway / Freeway**: Burnt orange `#BF5700` — this is your most visually distinctive choice
   - **Primary roads**: Terracotta `#C87A50`
   - **Secondary / local roads**: Warm grey `#B0A090`
   - **Paths / tracks**: Very light grey `#D4C8B8`
10. Enable road labels, colored white `#FFFFFF` for good contrast on the orange routes

**Add Place Labels:**

11. Click **"+ Add component"** → **"Place labels"**
12. Set label color to dark charcoal `#333333`
13. Font choice: **"Source Sans Pro"** or **"Roboto"** — both are clean, modern, and readable. Try **"Playfair Display"** for a more refined feel if you prefer.
14. Make state labels large, city labels medium, neighborhood labels small

**Add Land Use:**

15. Click **"+ Add component"** → **"Land use"**
16. Set park/recreation fill to warm olive `#9CAE85`
17. Set urban/built-up areas to light limestone `#E0D4B8`

**Add POI Labels:**

18. Click **"+ Add component"** → **"POI labels"**
19. Set POI icon/label color to burnt orange `#BF5700`
20. Keep sizes moderate — you don't want them competing with your winery markers

**Style Across Zoom Levels — This Is Important:**

The Texas Hill Country spans a large geographic area. Your map needs to look good both zoomed out (showing the full wine trail across the region) and zoomed in (showing individual winery parking lots).

21. Click on your **Road network** component
22. Click **"Style across zoom range"** and set:
    - At zoom 5–7: Show only motorways (I-10, US 290 corridor), hide local roads
    - At zoom 8–10: Show primary and secondary roads
    - At zoom 11+: Show all roads including local streets
23. Click on your **Place labels** component and set:
    - State labels: visible from zoom 4+
    - Major cities (Austin, San Antonio): zoom 6+
    - Small towns (Fredericksburg, Marble Falls): zoom 9+
    - Neighborhoods: zoom 12+
24. Test by zooming the preview map in and out to see how it transitions

**Publish and Get Your Style URL:**

25. Click **"Publish"** (top right)
26. Confirm in the dialog
27. Click **"Share"** → set to **"Public"**
28. Copy your **Style URL**:
    ```
    mapbox://styles/yourusername/clxabcdefghij1234567890
    ```
29. Keep this URL for Script 3

---

## Step 5: Run Script 3 — Map with Your UT Custom Style

### Part A: Add Credentials to Script 3

1. Open `scripts/03_map_custom_style.py`
2. Fill in the two variables:

```python
MAPBOX_TOKEN = "pk.eyJ1IjoieW91cnVzZXJuYW1l..."

MAPBOX_STYLE_URL = "mapbox://styles/yourusername/yourstyleid"
```

3. Save (**Ctrl+S**)

### Part B: Run the Script

```
python scripts/03_map_custom_style.py
```

Output: `data/tx_hill_wineries_map_custom.html`

Open it in the browser. Compare side by side:

- `data/tx_hill_wineries_map_basic.html` — plain OpenStreetMap
- `data/tx_hill_wineries_map_custom.html` — your UT Austin burnt orange style

Try zooming in on Fredericksburg to see your road hierarchy in action. Notice how the burnt orange freeways (US 290) guide the eye through the wine country corridor.

---

## Connection to Lab 6

| Today's Exercise | Lab 6 Equivalent |
|-----------------|------------------|
| Script 1 — server-side HTML scraping | Understanding data collection methods |
| Script 2 — Mapbox geocoding API | Exact same API call in Lab 6 |
| Folium popups with website links | Lab 6 requires image + description popups |
| Zoom-level styling in Step 4 | Lab 6 explicitly requires multi-scale styling |
| Script 3 — loading a custom Mapbox style | Lab 6 Part 3, the key technical skill |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` in the `200` folder |
| Script 1 finds fewer than 15 wineries | Website may have changed structure; try again or notify instructor |
| Script 2 can't find the CSV | Run Script 1 first |
| Map shows blank grey canvas | Check your Mapbox token and ensure your style is set to Public |
| Low geocoding success rate | Some rural addresses (county roads, FM roads) may not be in Mapbox's database — this is expected |
| Style URL not working | Confirm you copied `mapbox://styles/...` not the tile URL format |
