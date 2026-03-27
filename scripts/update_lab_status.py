import csv
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import io

# --- CONFIGURATION ---
CHANNEL_ID = "UC_Your_Actual_ID_Here" 
CSV_URL = "YOUR_FULL_GOOGLE_CSV_LINK_HERE" 
README_PATH = "README.md"

def get_latest_youtube_video():
    try:
        url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
        req = urllib.request.urlopen(url)
        root = ET.fromstring(req.read())
        ns = '{http://www.w3.org/2005/Atom}'
        entry = root.find(f'{ns}entry')
        title = entry.find(f'{ns}title').text
        link = entry.find(f'{ns}link').attrib['href']
        return title, link
    except:
        return "Latest Lab Report", "https://youtube.com/@truespeclab"

def get_upcoming_video():
    today = datetime.now()
    up_title, up_date = "System Telemetry", "TBD"
    
    try:
        response = urllib.request.urlopen(CSV_URL)
        content = response.read().decode('utf-8')
        lines = content.splitlines()
        reader = list(csv.reader(lines))
        
        month_idx, day_idx, title_idx = -1, -1, -1
        
        # Find headers: MONTH, DAY, and TITLE COPY
        for i, row in enumerate(reader):
            row_upper = [str(c).upper().strip() for c in row]
            if "MONTH" in row_upper and "DAY" in row_upper:
                month_idx = row_upper.index("MONTH")
                day_idx = row_upper.index("DAY")
                title_idx = row_upper.index("TITLE COPY") if "TITLE COPY" in row_upper else row_upper.index("TITLE")
                data_rows = reader[i+1:]
                break
        
        if month_idx != -1:
            for row in data_rows:
                if len(row) <= max(month_idx, day_idx, title_idx): continue
                m, d, t = row[month_idx].strip(), row[day_idx].strip(), row[title_idx].strip()
                
                if not m or not d or t == "0": continue

                try:
                    # Construct date for 2026
                    date_str = f"{d} {m} 2026"
                    parsed_date = datetime.strptime(date_str, "%d %B %Y")
                    
                    if parsed_date > today:
                        return t, parsed_date.strftime("%b %d").upper()
                except: continue
    except: pass
    return up_title, up_date

def update_readme():
    latest_title, latest_link = get_latest_youtube_video()
    up_title, up_date = get_upcoming_video()

    # The Clean Table
    new_table = (
        f"\n"
        f"| Research Area | Hardware / Device under Test | Status |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **LATEST REPORT** | [{latest_title}]({latest_link}) | `PUBLISHED` |\n"
        f"| **IN TEST BENCH** | {up_title} | `TARGET: {up_date}` |\n"
        f""
    )

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    header_marker = "### 🔬 Current Research Focus"
    
    if header_marker in content:
        keep_part = content.split(header_marker)[0] + header_marker
        tip = "\n\n> [!TIP] \n> Interested in the raw telemetry? Check the [/data](https://github.com/TrueSpecLab/telemetry-vault/tree/main/data) folder in the corresponding repository for the full .csv logs from these tests.\n\n"
        
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(keep_part + tip + new_table + "\n")

if __name__ == "__main__":
    update_readme()
