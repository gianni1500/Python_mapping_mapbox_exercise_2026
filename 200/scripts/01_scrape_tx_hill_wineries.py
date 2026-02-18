# =============================================================================
# SCRIPT 1 — Section 200: Scrape Texas Hill Country Wineries
# =============================================================================
# WHAT THIS SCRIPT DOES:
#   Visits the Texas Hill Country Wineries (THCW) member listing page and
#   extracts data on every member winery including:
#     - Name
#     - Street address, city, state, ZIP code
#     - Business hours
#     - Website URL
#     - Description
#
# SOURCE: https://texashillcountrywineries.org/pages/winery-listing-page
#
# OUTPUT: data/tx_hill_wineries.csv
#
# TO RUN:
#   python scripts/01_scrape_tx_hill_wineries.py
# =============================================================================


# =============================================================================
# STEP 1: IMPORT LIBRARIES
# =============================================================================

import requests          # Downloads the webpage
from bs4 import BeautifulSoup  # Parses the HTML into a searchable tree
import pandas as pd      # Organizes data into a table
import re                # Regular expressions for pattern-based text extraction
import os                # File/folder operations


# =============================================================================
# STEP 2: DEFINE SETTINGS
# =============================================================================

URL = "https://texashillcountrywineries.org/pages/winery-listing-page"

# Browser-like headers to avoid being blocked
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


# =============================================================================
# STEP 3: DOWNLOAD THE WEBPAGE
# =============================================================================
print("=" * 60)
print("  Texas Hill Country Wineries Scraper — Section 200")
print("=" * 60)
print(f"\nDownloading page: {URL}")

try:
    response = requests.get(URL, headers=HEADERS, timeout=30)
except requests.exceptions.ConnectionError:
    print("\nERROR: Cannot connect to the website. Check your internet connection.")
    exit()
except requests.exceptions.Timeout:
    print("\nERROR: Request timed out. Try again in a moment.")
    exit()

if response.status_code != 200:
    print(f"ERROR: Received status code {response.status_code}. Cannot proceed.")
    exit()

print(f"  Page downloaded successfully! (Status: {response.status_code})")


# =============================================================================
# STEP 4: PARSE THE HTML
# =============================================================================
print("\nParsing HTML...")

# BeautifulSoup turns the raw HTML text string into a navigable tree.
# Think of it like turning a large wall of text into an organized outline.
soup = BeautifulSoup(response.text, "lxml")
print("  HTML parsed.")


# =============================================================================
# STEP 5: LOCATE THE WINERY ENTRIES AND EXTRACT DATA
# =============================================================================
# The Texas Hill Country Wineries site (built on Shopify) lists each winery
# in a structured block with the name, address, hours, website, and description.
#
# Strategy:
#   1. Find the main content section of the page
#   2. Locate each winery block by searching for patterns in the text
#   3. Extract individual fields from each block
#
# The winery data structure we observed from the website:
#   [Winery Name]
#   [Street Address]
#   [City, State ZIP]
#   HOURS: [hours text]
#   [Visit Website link]
#   [Description text]

print("\nLocating winery entries...")

winery_list = []

# --- Strategy: Find All Winery "Cards" ---
# On the THCW site, winery entries appear to be individual blocks/divs.
# We'll search for container elements that hold both an address and a "Visit Website" link.
# This combination is unique to the winery entries (not navigation, footers, etc.)

# First, let's find all anchor tags linking to external websites (the "Visit Website" links)
# These are reliable anchors because every winery entry has one.
all_visit_links = soup.find_all("a", string=lambda text: text and "Visit Website" in text)

print(f"  Found {len(all_visit_links)} 'Visit Website' links — each one is a winery entry.")

for visit_link in all_visit_links:

    # --- Navigate to the Winery's Container Block ---
    # The THCW site (built on Shopify) uses a consistent card structure:
    #
    #   <div class="multicolumn-card__info">        ← full card
    #     [Winery Name text node / element]         ← name lives HERE
    #     <div class="rte typeset">                 ← address/hours/link live here
    #       [Street Address]
    #       [City, State ZIP]
    #       HOURS: ...
    #       <a href="...">Visit Website</a>
    #       [Description]
    #     </div>
    #   </div>
    #
    # Strategy:
    #   1. Walk up from the link to find div.multicolumn-card__info
    #   2. Compare its text to the inner rte div's text — the difference is the name
    #   3. Pull address/hours/description from the rte div lines

    # --- Step 1: Find the card container ---
    card_info = visit_link.find_parent("div", class_="multicolumn-card__info")
    if card_info is None:
        continue

    # --- Step 2: Find the inner content div (rte) ---
    # The rte div holds the address, hours, link, and description.
    rte_div = card_info.find("div", class_="rte")
    if rte_div is None:
        continue

    # Get lines from the full card and from the rte section separately
    card_lines = [l.strip() for l in card_info.get_text("\n").split("\n") if l.strip()]
    rte_lines  = [l.strip() for l in rte_div.get_text("\n").split("\n")  if l.strip()]
    rte_set    = set(rte_lines)   # fast lookup

    if len(card_lines) < 2:
        continue

    # --- Extract Winery Name ---
    # The name appears in card_info but NOT in the rte div — it's the only
    # piece of text that belongs to the outer card and not the inner content div.
    # We collect card lines that are absent from rte_set; the first one is the name.
    name_lines = [l for l in card_lines if l not in rte_set]
    name = name_lines[0] if name_lines else ""

    if not name or len(name) < 3:
        continue

    # --- Extract Website URL ---
    # We already have the "Visit Website" link — get its href attribute
    website = visit_link.get("href", "").strip()

    # --- Extract Hours ---
    # Work from the rte lines, since hours are inside the rte div
    hours = ""
    for line in rte_lines:
        # Hours lines typically start with "HOURS:"
        if line.upper().startswith("HOURS:") or line.upper().startswith("HOUR:"):
            hours = line.strip()
            break
        # Some entries use day names or "Open Daily" as the hours label
        if re.match(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun|Open|By Appt)", line, re.IGNORECASE):
            hours = line.strip()
            break

    # --- Extract Address, City, State, ZIP ---
    # The THCW site splits the address across multiple lines inside the rte div.
    # Two possible layouts observed:
    #
    #   Layout A (single line): "Johnson City, Texas 78636"
    #     → one line contains city, state, and ZIP
    #
    #   Layout B (split lines): "Johnson City, Texas"  then next line "78636"
    #     → city+state on one line, ZIP alone on the next line
    #
    # Strategy:
    #   1. Check each line for a standalone 5-digit ZIP code
    #   2. If found, look at the previous line for the "City, State" part
    #   3. The line before the city-state line is the street address
    street = ""
    city = ""
    state = ""
    zip_code = ""
    full_address = ""

    for i, line in enumerate(rte_lines):
        # --- Case A: "City, Texas NNNNN" or "City TX NNNNN" all on one line ---
        one_line_match = re.match(
            r"^(.+?),?\s+(Texas|TX)\s+(\d{5})$", line, re.IGNORECASE
        )
        if one_line_match:
            city     = one_line_match.group(1).strip()
            state    = "Texas"
            zip_code = one_line_match.group(3).strip()
            if i > 0:
                street = rte_lines[i - 1].strip()
            break

        # --- Case B: Standalone ZIP on its own line ---
        if re.match(r"^\d{5}$", line.strip()):
            zip_code = line.strip()
            # The previous line should be "City, Texas" or "City, TX"
            if i > 0:
                city_state_match = re.match(
                    r"^(.+?),?\s+(Texas|TX)$", rte_lines[i - 1], re.IGNORECASE
                )
                if city_state_match:
                    city  = city_state_match.group(1).strip()
                    state = "Texas"
                    # Street is the line before city-state
                    if i > 1:
                        street = rte_lines[i - 2].strip()
                else:
                    # Fallback: treat the previous line as city even without state label
                    city = rte_lines[i - 1].strip()
                    state = "Texas"
                    if i > 1:
                        street = rte_lines[i - 2].strip()
            break

    # Build full address string for geocoding
    if street and city and state and zip_code:
        full_address = f"{street}, {city}, {state} {zip_code}"
    elif city and state and zip_code:
        full_address = f"{city}, {state} {zip_code}"

    # --- Extract Description ---
    # The description (tagline + paragraph text) lives inside the rte div.
    # We skip the address lines, hours line, and "Visit Website" text —
    # anything left that is long enough is descriptive content.
    description_lines = []
    for line in rte_lines:
        # Skip the street address and city-state-zip lines
        if line == street:
            continue
        if line == f"{city}, Texas {zip_code}" or line == f"{city}, TX {zip_code}":
            continue
        if line.lower() == f"{city.lower()} texas {zip_code}" :
            continue
        # Skip hours and "Visit Website"
        if "Visit Website" in line or "View Website" in line:
            continue
        if line.upper().startswith("HOURS") or re.match(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)", line, re.IGNORECASE):
            continue
        # Substantial lines (>40 chars) are likely description text
        if len(line) > 40:
            description_lines.append(line)

    # Limit description to first 3 lines (most detailed, avoids overflow)
    description = " ".join(description_lines[:3]).strip()

    # --- Add to List ---
    winery_list.append({
        "Name": name,
        "Street_Address": street,
        "City": city,
        "State": state,
        "ZIP": zip_code,
        "Full_Address": full_address,
        "Hours": hours,
        "Website": website,
        "Description": description,
        "Source_URL": URL
    })

print(f"  Extracted {len(winery_list)} winery entries.")


# =============================================================================
# STEP 6: BUILD DATAFRAME AND CLEAN DATA
# =============================================================================
print("\nOrganizing and cleaning data...")

df = pd.DataFrame(winery_list)

# Remove duplicate winery names
df.drop_duplicates(subset=["Name"], keep="first", inplace=True)

# Remove entries with very short names (likely scraped by accident)
df = df[df["Name"].str.strip().str.len() >= 3].copy()

# Clean whitespace in all text columns
text_cols = ["Name", "Street_Address", "City", "State", "ZIP", "Hours", "Description"]
for col in text_cols:
    if col in df.columns:
        df[col] = df[col].str.strip()

print(f"  Total unique wineries: {len(df)}")

print("\n--- PREVIEW: First 3 rows ---")
print(df[["Name", "City", "ZIP", "Hours"]].head(3))


# =============================================================================
# STEP 7: SAVE TO CSV
# =============================================================================
os.makedirs("data", exist_ok=True)
output_path = os.path.join("data", "tx_hill_wineries.csv")
df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"\nData saved to: {output_path}")
print(f"Total wineries saved: {len(df)}")
print("\n" + "=" * 60)
print("  SCRIPT COMPLETE!")
print("=" * 60)
print("\nThis site was fully scrapable with requests + BeautifulSoup because")
print("the content is rendered server-side (no JavaScript rendering needed).")
print("Compare this to Script 1 from Section 1100 — a great illustration of")
print("the difference between static and dynamic websites.")
print("\nNext step: Run 02_geocode_map_basic.py")
print("  (Add your Mapbox token first!)")
