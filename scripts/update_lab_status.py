import csv
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import io

# --- CONFIGURATION ---
CHANNEL_ID = "UChy7QRfWL2mDN8seUqjD8tw" 
# Ensure this is the "Published to Web" CSV link for the SCHEDULE tab
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUahX8lrOmnF4JlJYKzuNVSnZZJAC8UoLhjKcmXRcy0MpRHbieAzLIAqoh9oEL1bgLYBVQuNVFsX1V/pub?gid=270845334&single=true&output=csv" 
README_PATH = "README.md"

def get_latest_youtube_video():
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
        req = urllib.request.urlopen(url)
        xml_data = req.read()
        root = ET.fromstring(xml_data)
        ns = '{http://www.w3.org/2005/Atom}'
        entry = root.find(f'{ns}entry')
        title = entry.find(f'{ns}title').text
        link = entry.find(f'{ns}link').attrib['href']
        return title, link
    except:
        return "Latest Lab Report", "https://youtube.com/truespeclab"

def get_upcoming_video():
    today = datetime.now()
    # Default fallback values
    upcoming_title = "Data Analysis"
    upcoming_date = "TBD"

    try:
        response = urllib.request.urlopen(CSV_URL)
        content = response.read().decode('utf-8')
        lines = content.splitlines()
        
        # We look for the row that contains 'CAMPAIGN' and 'DATE'
        reader = csv.reader(lines)
        found_header = False
        campaign_idx = -1
        date_idx = -1

        for row in reader:
            if not found_header:
                if "CAMPAIGN" in row and "DATE" in row:
                    campaign_idx = row.index("CAMPAIGN")
                    date_idx = row.index("DATE")
                    found_header = True
                continue
            
            # Now we are in the data rows
            if len(row) > max(campaign_idx, date_idx):
                title = row[campaign_idx].strip()
                date_str = row[date_idx].strip()
                
                if title and date_str:
                    try:
                        # Parsing format like "27-March"
                        clean_date = datetime.strptime(f"{date_str}-2026", "%d-%B-%Y")
                        if clean_date > today:
                            upcoming_title = title
                            upcoming_date = clean_date.strftime("%b %d").upper()
                            break # Found the first future date, stop here
                    except:
                        continue
    except Exception as e:
        print(f"CSV Fetch Error: {e}")
        
    return upcoming_title, upcoming_date

def update_readme():
    start_tag = ""
    end_tag = ""
    
    latest_title, latest_link = get_latest_youtube_video()
    up_title, up_date = get_upcoming_video()

    new_table = f"""| Project Category | Hardware Asset / Title | Status |
| :--- | :--- | :--- |
| **LATEST REPORT** | [{latest_title}]({latest_link}) | `PUBLISHED` |
| **IN TEST BENCH** | {up_title} | `TARGET: {up_date}` |
"""

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    if start_tag not in content or end_tag not in content:
        print("ERROR: Tags not found. Re-adding them to the end of the file.")
        # If the user deleted the tags, we append a fresh section to fix it
        final_content = content + f"\n\n### 🔬 Current Research Focus\n\n{start_tag}\n{new_table}{end_tag}\n"
    else:
        # Splitting logic to surgically replace ONLY the inside of the tags
        before = content.split(start_tag)[0]
        after = content.split(end_tag)[-1]
        final_content = f"{before}{start_tag}\n{new_table}{end_tag}{after}"

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(final_content.strip() + "\n")

if __name__ == "__main__":
    update_readme()
