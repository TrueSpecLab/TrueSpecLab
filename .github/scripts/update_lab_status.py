import csv
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import io
import time

# --- CONFIGURATION ---
CHANNEL_ID = "UChy7QRfWL2mDN8seUqjD8tw" 
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUahX8lrOmnF4JlJYKzuNVSnZZJAC8UoLhjKcmXRcy0MpRHbieAzLIAqoh9oEL1bgLYBVQuNVFsX1V/pub?gid=270845334&single=true&output=csv" 
README_PATH = "README.md"

def get_latest_youtube_video():
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    # Try up to 2 times if we hit a 500 error
    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                root = ET.fromstring(response.read())
                ns = '{http://www.w3.org/2005/Atom}'
                entry = root.find(f'{ns}entry')
                if entry is not None:
                    return entry.find(f'{ns}title').text, entry.find(f'{ns}link').attrib['href']
        except Exception as e:
            print(f"Attempt {attempt+1} - YouTube Error: {e}")
            time.sleep(2) # Wait 2 seconds before retrying
            
    return "Latest Lab Report", "https://youtube.com/@truespeclab"

def get_upcoming_video():
    today = datetime.now()
    # Default values if nothing is found
    final_t, final_d = "Calibration in Progress", "TBD"
    
    try:
        req = urllib.request.Request(CSV_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8')
            reader = list(csv.reader(io.StringIO(content)))
            
            # Identify columns
            headers = [h.upper().strip() for h in reader[0]]
            m_idx = headers.index("MONTH") if "MONTH" in headers else -1
            d_idx = headers.index("DAY") if "DAY" in headers else -1
            # Try TITLE COPY first, then fallback to CAMPAIGN
            t_idx = headers.index("TITLE COPY") if "TITLE COPY" in headers else (headers.index("CAMPAIGN") if "CAMPAIGN" in headers else -1)

            if -1 not in (m_idx, d_idx, t_idx):
                for row in reader[1:]:
                    if len(row) <= max(m_idx, d_idx, t_idx): continue
                    m, d, t = row[m_idx].strip(), row[d_idx].strip(), row[t_idx].strip()
                    
                    if not m or not d or not t or t == "0": continue

                    try:
                        # Validate the date
                        date_obj = datetime.strptime(f"{d} {m} 2026", "%d %B %Y")
                        if date_obj > today:
                            return t, date_obj.strftime("%b %d").upper()
                    except: continue
    except Exception as e:
        print(f"Sheets Error: {e}")
        
    return final_t, final_d

def update_readme():
    latest_title, latest_link = get_latest_youtube_video()
    up_title, up_date = get_upcoming_video()

    new_table = (
        f"| Research Area | Hardware / Device under Test | Status |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **LATEST REPORT** | [{latest_title}]({latest_link}) | `PUBLISHED` |\n"
        f"| **IN TEST BENCH** | {up_title} | `TARGET: {up_date}` |\n"
    )

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    marker = "### 🔬 Current Research Focus"
    if marker in content:
        # Rebuild the bottom half fresh to prevent duplication
        clean_top = content.split(marker)[0] + marker
        tip = "\n\n> [!TIP] \n> Interested in the raw telemetry? Check the [/data](https://github.com/TrueSpecLab/telemetry-vault/tree/main/data) folder in the corresponding repository for the full .csv logs from these tests.\n\n"
        
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(clean_top + tip + new_table + "\n")

if __name__ == "__main__":
    update_readme()
