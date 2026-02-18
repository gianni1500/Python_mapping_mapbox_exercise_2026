# =============================================================================
# SCRIPT 1 — Section 930: Scrape Napa Valley Winery Data
# =============================================================================
# WHAT THIS SCRIPT DOES:
#   Visits the Fort Ross Conservancy's Napa Valley AVA Winery List page and
#   extracts the name, phone number, and address of every winery listed.
#   The results are saved as a CSV file for use in the next script.
#
# SOURCE: https://www.fortross.org/local/ava/napa-valley
#
# OUTPUT: data/napa_wineries.csv
#   Columns: Name, Phone, Full_Address, City, State, ZIP, Source_URL
#
# TO RUN THIS SCRIPT:
#   In the VS Code terminal, navigate to the 930 folder and run:
#       python scripts/01_scrape_napa_wineries.py
# =============================================================================


# =============================================================================
# STEP 1: IMPORT LIBRARIES
# =============================================================================
# Before we can use any extra tools, we need to "import" (load) them.
# Think of imports like opening a toolbox before starting a project.

import requests          # 'requests' lets Python send web requests and download pages
from bs4 import BeautifulSoup  # 'BeautifulSoup' reads/parses raw HTML into a searchable tree
import pandas as pd     # 'pandas' organizes data into rows and columns, like a spreadsheet
import re               # 're' (regular expressions) finds patterns inside text strings
import os               # 'os' handles folders and file paths on your computer


# =============================================================================
# STEP 2: DEFINE SETTINGS
# =============================================================================
# Store our target URL and request headers in variables at the top of the
# script. This makes it easy to change them in one place if needed.

# The URL of the page we want to scrape
URL = "https://www.fortross.org/local/ava/napa-valley"

# When Python sends a request to a website, it identifies itself with a
# "User-Agent" string. By default, Python's user-agent looks like a bot,
# and some websites block bots. Setting a browser-like User-Agent makes
# our request look like it comes from a real person using Chrome.
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
print("  Napa Valley Winery Scraper")
print("=" * 60)
print(f"\nStep 1: Downloading page from: {URL}")
print("  (This may take a few seconds...)")

# requests.get() sends a GET request to the URL — the same thing your browser
# does when you type an address into the address bar and press Enter.
# We also pass our headers and set a timeout of 30 seconds.
try:
    response = requests.get(URL, headers=HEADERS, timeout=30)
except requests.exceptions.ConnectionError:
    # This error means we couldn't connect — check your internet connection
    print("\nERROR: Could not connect to the website.")
    print("Please check your internet connection and try again.")
    exit()
except requests.exceptions.Timeout:
    # This error means the website took too long to respond
    print("\nERROR: The website took too long to respond (timed out after 30s).")
    exit()

# response.status_code tells us if the download was successful.
# HTTP 200 means "OK". Other codes indicate errors (e.g., 404 = Not Found).
if response.status_code != 200:
    print(f"\nERROR: Received unexpected status code: {response.status_code}")
    print("The website may be temporarily unavailable. Try again later.")
    exit()

print(f"  SUCCESS — Page downloaded. (HTTP Status: {response.status_code})")


# =============================================================================
# STEP 4: PARSE THE HTML
# =============================================================================
print("\nStep 2: Parsing the HTML...")

# response.text contains the raw HTML of the page as one giant text string.
# BeautifulSoup reads that string and creates a searchable tree structure
# so we can find specific tags like <h3>, <a>, <div>, etc.
# "lxml" is the parser engine — it's fast and handles messy HTML well.
soup = BeautifulSoup(response.text, "lxml")

print("  HTML parsed successfully.")


# =============================================================================
# STEP 5: LOCATE WINERY ENTRIES AND EXTRACT DATA
# =============================================================================
print("\nStep 3: Extracting winery data...")

# On this page, every winery name is wrapped in an <h3> tag.
# soup.find_all("h3") returns a list of ALL <h3> elements on the page.
all_h3_tags = soup.find_all("h3")

print(f"  Found {len(all_h3_tags)} <h3> tags on the page.")
print("  Looping through each one to extract data...")

# We will build a list of dictionaries. Each dictionary = one winery's data.
# At the end, we'll convert this list into a pandas DataFrame (table).
winery_list = []

# Loop through every <h3> tag found on the page
for h3_tag in all_h3_tags:

    # --- Extract the Winery Name ---
    # .get_text() reads all the visible text inside the tag.
    # strip=True removes leading/trailing spaces and newlines.
    name = h3_tag.get_text(strip=True)

    # Some h3 tags might be section headers or page titles, not winery names.
    # Skip any that are blank or very short (less than 3 characters).
    if not name or len(name) < 3:
        continue

    # --- Navigate to the Winery's Container ---
    # Each winery's name, phone, and address are grouped inside a parent
    # container element (a <div> or <li> or similar). By going "up" to the
    # parent, we can search within just that winery's block of HTML.
    # We try going up 2 levels to catch the full winery card.
    parent_container = h3_tag.find_parent()  # Go up one level
    if parent_container:
        grandparent = parent_container.find_parent()
        if grandparent:
            parent_container = grandparent  # Use the grandparent for broader search

    # --- Extract Phone Number ---
    phone = ""  # Start with empty string in case there's no phone

    if parent_container:
        # In HTML, phone links look like: <a href="tel:707-942-6446">Phone</a>
        # We use find() to search for an <a> tag whose href starts with "tel:"
        # The lambda function checks each href value: "does it start with 'tel:'?"
        phone_anchor = parent_container.find(
            "a", href=lambda href: href and href.startswith("tel:")
        )
        if phone_anchor:
            # href attribute contains "tel:707-942-6446"
            # We strip off the "tel:" prefix to get just the number
            phone = phone_anchor["href"].replace("tel:", "").strip()

    # --- Extract Address ---
    full_address = ""
    city = ""
    state = ""
    zip_code = ""

    if parent_container:
        # Get all the text inside the container, using newlines as separators.
        # This gives us a multi-line string we can split and search line by line.
        container_text = parent_container.get_text(separator="\n")

        # Split the text into individual lines and remove blank lines
        lines = [line.strip() for line in container_text.split("\n") if line.strip()]

        # Look for the line that contains "Address" — the actual address text
        # usually appears immediately after it
        for i, line in enumerate(lines):
            # Check if this line is or contains the "Address" label
            if line.strip() == "Address" or line.strip().startswith("Address"):
                # The address is on the NEXT line
                if i + 1 < len(lines):
                    full_address = lines[i + 1].strip()
                break  # Stop looking once we've found it

    # --- Parse City, State, ZIP from the Full Address ---
    # The address format is generally: "Street City, State ZIP"
    # Examples:
    #   "3250 Highway 128 Calistoga, California 94515"
    #   "1700 Wooden Valley Rd Napa, California 94558"
    #   "P.O. Box 10307 Napa, California 94581"
    #   "Napa, California"  (city only, no street)
    #
    # Strategy: Find the LAST comma — everything after it is "State ZIP",
    # everything before the last comma ends with the city name.

    if full_address:
        last_comma_pos = full_address.rfind(",")  # rfind() finds LAST occurrence

        if last_comma_pos != -1:
            # Everything after the last comma: " California 94558" or " California"
            after_comma = full_address[last_comma_pos + 1:].strip()

            # Split "California 94558" into state and ZIP
            # re.split() with max split of 1 separates on the LAST space
            state_zip_parts = after_comma.rsplit(None, 1)  # rsplit from right, max 1 split

            if len(state_zip_parts) == 2:
                # Check if the second part looks like a ZIP code (5 digits)
                if re.match(r"^\d{5}$", state_zip_parts[1]):
                    state = state_zip_parts[0].strip()
                    zip_code = state_zip_parts[1].strip()
                else:
                    # No ZIP code found — treat the whole thing as state
                    state = after_comma.strip()
            else:
                state = after_comma.strip()

            # Everything BEFORE the last comma: "Street City" or just "City"
            before_comma = full_address[:last_comma_pos].strip()

            # The LAST word(s) before the comma are the city name.
            # Cities can be multi-word (e.g., "St. Helena", "Pope Valley").
            # We look for known city patterns by splitting from the right.
            # Common multi-word city endings in Napa region:
            city_pattern = re.search(
                r"([A-Za-z][a-z]+(?:\s+[A-Za-z][a-z.]+)*)$", before_comma
            )
            if city_pattern:
                city = city_pattern.group(1).strip()

    # --- Add This Winery to Our List ---
    # Only add if we have at least a name (address may be incomplete for some)
    winery_list.append({
        "Name": name,
        "Phone": phone,
        "Full_Address": full_address,
        "City": city,
        "State": state,
        "ZIP": zip_code,
        "Source_URL": URL
    })


# =============================================================================
# STEP 6: BUILD THE DATAFRAME AND CLEAN THE DATA
# =============================================================================
print("\nStep 4: Organizing and cleaning the data...")

# Convert our list of dictionaries into a pandas DataFrame.
# A DataFrame is like a spreadsheet: rows = wineries, columns = data fields.
df = pd.DataFrame(winery_list)

print(f"  Total entries before cleaning: {len(df)}")

# --- Remove Duplicates ---
# The webpage sometimes renders the same list multiple times (e.g., for
# mobile vs. desktop views). drop_duplicates() removes any rows where the
# 'Name' column appears more than once, keeping only the first occurrence.
df.drop_duplicates(subset=["Name"], keep="first", inplace=True)

# --- Remove Obvious Non-Winery Entries ---
# Filter out any entries with blank names or names shorter than 3 characters
df = df[df["Name"].str.strip().str.len() >= 3].copy()

# --- Strip Extra Whitespace from All Text Columns ---
# This cleans up any accidental spaces that might have been captured
for col in ["Name", "Phone", "Full_Address", "City", "State", "ZIP"]:
    df[col] = df[col].str.strip()

print(f"  Total entries after cleaning: {len(df)}")

# Show a preview of what we found
print("\n--- PREVIEW: First 5 rows ---")
print(df[["Name", "Phone", "City", "State"]].head())
print("...")


# =============================================================================
# STEP 7: SAVE TO CSV
# =============================================================================
print("\nStep 5: Saving data to CSV...")

# os.makedirs() creates the 'data' folder if it doesn't already exist.
# exist_ok=True means "don't throw an error if the folder already exists"
os.makedirs("data", exist_ok=True)

# Define the output file path
output_path = os.path.join("data", "napa_wineries.csv")

# to_csv() saves the DataFrame as a comma-separated values file.
# index=False means don't write the row numbers (0, 1, 2...) to the file.
df.to_csv(output_path, index=False, encoding="utf-8-sig")
# encoding="utf-8-sig" ensures special characters (accented letters) display
# correctly if you open the file in Excel.

print(f"  Data saved to: {output_path}")
print(f"  Total wineries saved: {len(df)}")
print("\n" + "=" * 60)
print("  SCRIPT COMPLETE!")
print("=" * 60)
print("\nNext step: Run script 02_geocode_map_basic.py")
print("  (Remember to add your Mapbox access token to that script first!)")
