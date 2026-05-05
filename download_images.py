import requests
import os
import time

os.makedirs("images", exist_ok=True)

# Use Wikipedia REST API to get the official thumbnail for each location
locations = {
    "liberty_state_park.jpg":    "Liberty_State_Park",
    "liberty_science_center.jpg": "Liberty_Science_Center",
    "princeton_university.jpg":  "Princeton_University",
    "six_flags.jpg":             "Six_Flags_Great_Adventure",
    "point_pleasant.jpg":        "Point_Pleasant_Beach,_New_Jersey",
    "grounds_for_sculpture.jpg": "Grounds_for_Sculpture",
    "branch_brook_park.jpg":     "Branch_Brook_Park",
    "american_dream_mall.jpg":   "American_Dream_Meadowlands",
    "stone_pony.jpg":            "Stone_Pony",
    "asbury_park.jpg":           "Asbury_Park,_New_Jersey",
}

headers = {
    "User-Agent": "HomemapPortfolioProject/1.0 (educational; contact: student@school.edu)"
}

print("Fetching images via Wikipedia REST API...\n")

for filename, wiki_title in locations.items():
    dest = os.path.join("images", filename)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        print(f"  Already exists: {filename}")
        continue

    try:
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_title}"
        resp = requests.get(api_url, headers=headers, timeout=15)

        if resp.status_code != 200:
            print(f"  API FAILED ({resp.status_code}): {wiki_title}")
            time.sleep(1)
            continue

        data = resp.json()
        img_url = None

        if "originalimage" in data:
            img_url = data["originalimage"]["source"]
        elif "thumbnail" in data:
            img_url = data["thumbnail"]["source"]

        if not img_url:
            print(f"  No image found for: {wiki_title}")
            continue

        img_resp = requests.get(img_url, headers=headers, timeout=20)
        if img_resp.status_code == 200:
            with open(dest, "wb") as f:
                f.write(img_resp.content)
            size_kb = len(img_resp.content) // 1024
            print(f"  Downloaded: {filename} ({size_kb} KB)  <- {wiki_title}")
        else:
            print(f"  Image download failed ({img_resp.status_code}): {filename}")

    except Exception as e:
        print(f"  ERROR: {filename} --- {e}")

    time.sleep(0.5)

print("\nDone! Images saved to ./images/")
