import csv
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import io

# --- CONFIGURATION ---
CHANNEL_ID = "UChy7QRfWL2mDN8seUqjD8tw" 
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUahX8lrOmnF4JlJYKzuNVSnZZJAC8UoLhjKcmXRcy0MpRHbieAzLIAqoh9oEL1bgLYBVQuNVFsX1V/pub?gid=270845334&single=true&output=csv" 
README_PATH = "README.md"

def get_latest_youtube_video():
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    # This header is the secret sauce. Without it, YouTube often returns a 404 or 403.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_content = response.read()
            root = ET.fromstring(xml_content)
            ns = '{http://www.w3.org/2005/Atom}'
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
        # Google Sheets usually doesn't block bots, but we use headers just in case
        req = urllib.request.Request(CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8')
        lines = content.splitlines()
        reader = list(csv.reader(lines))
        
        month_idx, day_idx, title_idx = -1, -1, -1
        
        for i, row in enumerate(reader):
            row_upper = [str(c).upper().strip() for c in row]
            if "MONTH" in row_upper and "DAY" in row_upper:
                month_idx = row_upper.index("MONTH")
                day_idx = row_upper.index("DAY")
                title_idx = row_upper.index("TITLE COPY") if "TITLE COPY" in row_upper else row_upper.index("CAMPAIGN")
                data_rows = reader[i+1:]
                break
        
        if month_idx != -1:
            for row in data_rows:
                if len(row) <= max(month_idx, day_idx, title_idx): continue
                m, d, t = row[month_idx].strip(), row[day_idx].strip(), row[title_idx].strip()
                if not m or not d or t == "0": continue

                try:
                    date_str = f"{d} {m} 2026"
                    parsed_date = datetime.strptime(date_str, "%d %B %Y")
                    if parsed_date > today:
                        return t, parsed_date.strftime("%b %d").upper()
                except: continue
    except Exception as e:
        print(f"DEBUG Sheets Error: {e}")
        
    return up_title, up_date

def update_readme():
    latest_title, latest_link = get_latest_youtube_video()
    up_title, up_date = get_upcoming_video()

    new_table = (
        f"\n| Research Area | Hardware / Device under Test | Status |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **LATEST REPORT** | [{latest_title}]({latest_link}) | `PUBLISHED` |\n"
        f"| **IN TEST BENCH** | {up_title} | `TARGET: {up_date}` |\n"
    )

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    marker = "### 🔬 Current Research Focus"
    
    if marker in content:
        # 1. Take everything BEFORE the marker
        # 2. Add the marker back
        # 3. Add the static tip
        # 4. Add the fresh table
        # This completely discards any old tables or duplicates.
        base_part = content.split(marker)[0] + marker
        tip = "\n\n> [!TIP] \n> Interested in the raw telemetry? Check the [/data](https://github.com/TrueSpecLab/telemetry-vault/tree/main/data) folder in the corresponding repository for the full .csv logs from these tests.\n"
        
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(base_part + tip + new_table)
    else:
        print(f"ERROR: Marker '{marker}' not found.")

if __name__ == "__main__":
    update_readme()
