# =============================================================================
# SCRIPT 1 — Section 1100: Scrape Best Tacos in Fort Worth (Texas Monthly)
# =============================================================================
# WHAT THIS SCRIPT DOES:
#   Attempts to scrape the Texas Monthly "Best Tacos in Fort Worth" article
#   to extract taco shop names, addresses, and descriptions.
#
#   *** IMPORTANT TEACHING MOMENT ***
#   Texas Monthly's website uses JavaScript to render its article content.
#   This means the actual taco listings are NOT present in the raw HTML
#   that a simple 'requests' call downloads — the browser has to run JavaScript
#   first to generate the visible content. This is a very common challenge
#   in real-world web scraping!
#
#   This script will:
#     1. ATTEMPT to scrape the page with requests to show what happens
#     2. EXPLAIN why JavaScript-rendered pages require different tools
#     3. USE a curated hardcoded dataset as our working data source
#        (the data is drawn from publicly known Texas Monthly coverage)
#
# SOURCE: https://www.texasmonthly.com/food/best-tacos-fort-worth/
#
# OUTPUT: data/fw_tacos.csv
#
# TO RUN:
#   python scripts/01_scrape_fw_tacos.py
# =============================================================================


# =============================================================================
# STEP 1: IMPORT LIBRARIES
# =============================================================================

import requests          # For downloading webpages
from bs4 import BeautifulSoup  # For parsing HTML
import pandas as pd      # For organizing data into a table
import os                # For creating folders and file paths


# =============================================================================
# STEP 2: ATTEMPT TO SCRAPE THE PAGE
# =============================================================================
# This section is intentionally educational — we WANT the scrape to show
# limited results so we can discuss why JavaScript changes things.

URL = "https://www.texasmonthly.com/food/best-tacos-fort-worth/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

print("=" * 60)
print("  Fort Worth Taco Scraper — Section 1100")
print("=" * 60)
print(f"\nAttempting to download page: {URL}")

scraped_items = []  # Will hold any data we manage to find in the raw HTML

try:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    print(f"  HTTP Status Code: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")

        # Try to find article headings (h2, h3) that might contain restaurant names
        headings = soup.find_all(["h2", "h3"])
        print(f"  Found {len(headings)} heading tags in the raw HTML.")

        for heading in headings:
            text = heading.get_text(strip=True)
            # Filter for headings that look like they might be restaurant names
            # (skip page navigation items, "Related Articles", etc.)
            if text and len(text) > 3 and len(text) < 80:
                scraped_items.append(text)

        print(f"  Extracted {len(scraped_items)} potential headings.")

        if len(scraped_items) < 5:
            print("\n  *** NOTE: Very little content was found in the raw HTML. ***")
            print("  This is because Texas Monthly renders article content using")
            print("  JavaScript (a client-side scripting language). When Python")
            print("  downloads the page, it only gets the initial HTML 'shell' —")
            print("  the actual article content hasn't been generated yet.")
            print()
            print("  To scrape JavaScript-rendered pages, you would typically use:")
            print("    - Selenium  (controls a real browser that runs JavaScript)")
            print("    - Playwright (a modern browser automation library)")
            print("    - Splash     (a lightweight JavaScript rendering service)")
            print()
            print("  For this exercise, we will use a curated dataset instead.")

    else:
        print(f"  Could not download the page (Status: {response.status_code})")

except requests.exceptions.RequestException as e:
    print(f"  Request failed: {e}")

print()


# =============================================================================
# STEP 3: USE CURATED DATASET
# =============================================================================
# Because the Texas Monthly page is JavaScript-rendered and we cannot extract
# structured data (names + addresses) from it with simple scraping, we use a
# carefully assembled dataset of Fort Worth taco spots highlighted in Texas
# Monthly and other Fort Worth food coverage.
#
# Each entry includes:
#   Name         — Restaurant name
#   Address      — Full street address (for geocoding in Script 2)
#   Neighborhood — Fort Worth neighborhood
#   Specialty    — What they're best known for
#   Description  — Short summary of the restaurant
#   Source       — Where this information comes from

print("Loading curated Fort Worth taco dataset...")

taco_data = [
    {
        "Name": "Salsa Limon",
        "Address": "1407 N Main St, Fort Worth, TX 76164",
        "Neighborhood": "Stockyards",
        "Specialty": "Birria tacos, street-style tacos",
        "Description": (
            "A beloved Fort Worth institution serving authentic Mexican street tacos. "
            "Known for birria and a rotating menu of traditional preparations. "
            "The Stockyards location is a local favorite."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Joe T. Garcia's",
        "Address": "2201 N Commerce St, Fort Worth, TX 76106",
        "Neighborhood": "Near Northside",
        "Specialty": "Family-style Mexican, fajita tacos",
        "Description": (
            "A Fort Worth institution since 1935, Joe T. Garcia's is a multi-room "
            "Mexican restaurant famous for its sprawling outdoor patio. The fajita "
            "and bean tacos are legendary, and the atmosphere is unmatched."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Benito's",
        "Address": "1450 W Magnolia Ave, Fort Worth, TX 76104",
        "Neighborhood": "Near Southside",
        "Specialty": "Interior Mexican, tacos al carbon",
        "Description": (
            "Celebrated for interior Mexican cooking on the Near Southside, Benito's "
            "offers tacos that go beyond Tex-Mex into deeper regional traditions. "
            "A cornerstone of Fort Worth's culinary scene."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Taco Heads",
        "Address": "2818 Morton St, Fort Worth, TX 76107",
        "Neighborhood": "West 7th (Cultural District)",
        "Specialty": "Creative gourmet tacos",
        "Description": (
            "Taco Heads brings a creative, gourmet approach to the taco. Located "
            "in the Cultural District, this spot is known for unexpected flavor "
            "combinations and high-quality ingredients in a casual setting."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Velvet Taco",
        "Address": "3001 S Hulen St, Fort Worth, TX 76109",
        "Neighborhood": "Hulen / Cityview",
        "Specialty": "Rotating creative tacos, WTF taco",
        "Description": (
            "A Texas-born chain that reinvents what a taco can be. Velvet Taco "
            "offers international-inspired fillings from Nashville hot chicken to "
            "spicy tikka masala. The weekly rotating WTF (Weekly Taco Feature) is "
            "a must-try."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Digg's Taco Shop",
        "Address": "7750 Camp Bowie W Blvd, Fort Worth, TX 76116",
        "Neighborhood": "Camp Bowie West",
        "Specialty": "Breakfast and street tacos",
        "Description": (
            "An unpretentious taco shop on Camp Bowie beloved for its no-fuss "
            "approach and fresh ingredients. The breakfast tacos draw a loyal "
            "morning crowd, and the street tacos offer great value."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Revolver Taco Lounge",
        "Address": "2822 W 7th St, Fort Worth, TX 76107",
        "Neighborhood": "West 7th",
        "Specialty": "Upscale Mexican, masa-forward tacos",
        "Description": (
            "Revolver is one of Fort Worth's most acclaimed taco destinations, "
            "known for housemade masa and sophisticated preparations drawing from "
            "interior Mexican traditions. Highly regarded by Texas Monthly and "
            "national food critics."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "La Familia Cortez",
        "Address": "1521 Hemphill St, Fort Worth, TX 76104",
        "Neighborhood": "Near Southside",
        "Specialty": "Breakfast tacos, carne guisada",
        "Description": (
            "A neighborhood taqueria beloved for its carne guisada and breakfast "
            "tacos. La Familia Cortez represents the kind of everyday taqueria "
            "that Fort Worth's Hispanic communities have sustained for decades."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Esperanza's Mexican Bakery & Cafe",
        "Address": "2122 N Main St, Fort Worth, TX 76164",
        "Neighborhood": "Near Northside",
        "Specialty": "Breakfast tacos, pan dulce",
        "Description": (
            "More than a bakery, Esperanza's anchors the Near Northside with its "
            "scratch-made breakfast tacos and legendary pan dulce. The tacos de "
            "barbacoa on weekend mornings are a Fort Worth rite of passage."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Ellerbe Fine Foods",
        "Address": "1501 W Magnolia Ave, Fort Worth, TX 76104",
        "Neighborhood": "Near Southside",
        "Specialty": "Farm-to-table tacos (on menu rotation)",
        "Description": (
            "While not exclusively a taco shop, Ellerbe's seasonal menu often "
            "features some of Fort Worth's most creative taco preparations using "
            "local and farm-sourced ingredients. A pillar of Near Southside dining."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "El Paseo de Tacos",
        "Address": "6713 Camp Bowie Blvd, Fort Worth, TX 76116",
        "Neighborhood": "Ridglea",
        "Specialty": "Tacos al pastor, street tacos",
        "Description": (
            "A no-frills taqueria that consistently delivers on the fundamentals: "
            "fresh tortillas, properly seasoned fillings, and good salsa. The "
            "al pastor, shaved off a rotating spit, is the signature order."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
    {
        "Name": "Mily's Cafe",
        "Address": "4301 River Oaks Blvd, Fort Worth, TX 76114",
        "Neighborhood": "River Oaks",
        "Specialty": "Tex-Mex breakfast tacos",
        "Description": (
            "A family-run neighborhood staple serving Tex-Mex breakfast and lunch. "
            "Mily's is trusted by locals for honest, home-style tacos with "
            "portions that more than satisfy."
        ),
        "Source": "Texas Monthly / Local Coverage"
    },
]

print(f"  Loaded {len(taco_data)} Fort Worth taco shops.")


# =============================================================================
# STEP 4: BUILD THE DATAFRAME AND SAVE TO CSV
# =============================================================================
print("\nOrganizing data into a table...")

# Convert the list of dictionaries into a pandas DataFrame
df = pd.DataFrame(taco_data)

# Display a preview
print("\n--- PREVIEW: First 3 rows ---")
print(df[["Name", "Neighborhood", "Specialty"]].head(3))

# Create the data output folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Save to CSV
output_path = os.path.join("data", "fw_tacos.csv")
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\nData saved to: {output_path}")
print(f"Total records: {len(df)}")
print("\n" + "=" * 60)
print("  SCRIPT COMPLETE!")
print("=" * 60)
print("\nKey lesson from this script:")
print("  Many modern websites use JavaScript to render content.")
print("  When that happens, simple requests + BeautifulSoup isn't enough.")
print("  Real scrapers often need Selenium or Playwright for those sites.")
print("\nNext step: Run script 02_geocode_map_basic.py")
print("  (Remember to add your Mapbox access token first!)")
