import csv
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import io

# --- CONFIGURATION ---
CHANNEL_ID = "UChy7QRfWL2mDN8seUqjD8tw" 
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUahX8lrOmnF4JlJYKzuNVSnZZJAC8UoLhjKcmXRcy0MpRHbieAzLIAqoh9oEL1bgLYBVQuNVFsX1V/pub?gid=270845334&single=true&output=csv" 
README_PATH = "README.md"

START_TAG = "".join(["<", "!", "--", " RESEARCH-TABLE:START ", "--", ">"])
END_TAG = "".join(["<", "!", "--", " RESEARCH-TABLE:END ", "--", ">"])

def get_latest_youtube_video():
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
        # Spoof a standard web browser to bypass YouTube's basic bot blocks
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        ns = '{http://www.w3.org/2005/Atom}'
        
        # Extract the very first video entry
        entry = root.find(f'{ns}entry')
        if entry is not None:
            title = entry.find(f'{ns}title').text
            link = entry.find(f'{ns}link').attrib['href']
            return title, link
    except Exception as e:
        print(f"DEBUG YouTube Error: {e}")
        
    return "Latest Lab Report", "https://youtube.com/@truespeclab"

def get_upcoming_video():
    today = datetime.now()
    up_title, up_date = "System Telemetry", "TBD"
    
    try:
        response = urllib.request.urlopen(CSV_URL)
        content = response.read().decode('utf-8')
        lines = content.splitlines()
        reader = list(csv.reader(lines))
        
        # New Column Mapping based on your DEBUG logs
        month_idx = -1
        day_idx = -1
        title_idx = -1
        
        for i, row in enumerate(reader):
            row_upper = [str(c).upper().strip() for c in row]
            # Match the headers from your log
            if "MONTH" in row_upper and "DAY" in row_upper:
                month_idx = row_upper.index("MONTH")
                day_idx = row_upper.index("DAY")
                # Look for TITLE COPY or CAMPAIGN
                if "TITLE COPY" in row_upper:
                    title_idx = row_upper.index("TITLE COPY")
                elif "CAMPAIGN" in row_upper:
                    title_idx = row_upper.index("CAMPAIGN")
                
                data_rows = reader[i+1:]
                break
        
        if month_idx != -1 and day_idx != -1:
            for row in data_rows:
                if len(row) <= max(month_idx, day_idx, title_idx): continue
                
                month_val = row[month_idx].strip()
                day_val = row[day_idx].strip()
                title_val = row[title_idx].strip()
                
                if not month_val or not day_val or not title_val: continue
                if title_val == "0": continue # Skip placeholder rows

                try:
                    # Construct date: e.g., "March 27 2026"
                    date_str = f"{day_val} {month_val} 2026"
                    parsed_date = datetime.strptime(date_str, "%d %B %Y")
                    
                    if parsed_date > today:
                        return title_val, parsed_date.strftime("%b %d").upper()
                except:
                    continue
    except Exception as e:
        print(f"DEBUG Error: {e}")
        
    return up_title, up_date

def update_readme():
    latest_title, latest_link = get_latest_youtube_video()
    up_title, up_date = get_upcoming_video()

    # Define the fresh table with tags included
    new_table_block = (
        f"\n"
        f"| Research Area | Hardware / Device under Test | Status |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **LATEST REPORT** | [{latest_title}]({latest_link}) | `PUBLISHED` |\n"
        f"| **IN TEST BENCH** | {up_title} | `TARGET: {up_date}` |\n"
        f""
    )

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # FAIL-SAFE: We split at the last known 'safe' header.
    # This prevents duplication because we discard EVERYTHING after this marker.
    marker = "### 🔬 Current Research Focus"
    
    if marker in content:
        # Keep everything up to and including the header
        base_content = content.split(marker)[0] + marker
        
        # Re-add the static tip and the fresh table
        tip = "\n\n> [!TIP] \n> Interested in the raw telemetry? Check the [/data](https://github.com/TrueSpecLab/telemetry-vault/tree/main/data) folder in the corresponding repository for the full .csv logs from these tests.\n\n"
        
        final_output = base_content + new_table_block + tip
        
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(final_output.strip() + "\n")
    else:
        print(f"CRITICAL ERROR: Marker '{marker}' not found. README was not modified.")

if __name__ == "__main__":
    update_readme()
