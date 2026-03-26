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
        print(f"DEBUG: Fetching CSV from {CSV_URL[:50]}...")
        response = urllib.request.urlopen(CSV_URL)
        content = response.read().decode('utf-8')
        lines = content.splitlines()
        
        # DEBUG: Print the first 3 lines of the CSV to the GitHub Action Log
        print("DEBUG: CSV Header Check:")
        for line in lines[:5]: print(f"  > {line}")

        reader = list(csv.reader(lines))
        camp_idx, date_idx = -1, -1
        
        for i, row in enumerate(reader):
            row_upper = [str(c).upper().strip() for c in row]
            if "CAMPAIGN" in row_upper and "DATE" in row_upper:
                camp_idx = row_upper.index("CAMPAIGN")
                date_idx = row_upper.index("DATE")
                print(f"DEBUG: Found Headers at row {i}. Campaign Col: {camp_idx}, Date Col: {date_idx}")
                data_rows = reader[i+1:]
                break
        
        if camp_idx != -1:
            for row in data_rows:
                if len(row) <= max(camp_idx, date_idx): continue
                title = row[camp_idx].strip()
                date_val = row[date_idx].strip()
                
                if not title or not date_val: continue
                
                # Check for "27-March" or "27-Mar"
                for fmt in ["%d-%B-%Y", "%d-%b-%Y", "%m/%d/%Y"]:
                    try:
                        test_str = date_val if "2026" in date_val else f"{date_val}-2026"
                        parsed_date = datetime.strptime(test_str, fmt)
                        if parsed_date > today:
                            print(f"DEBUG: Found Match! {title} on {parsed_date}")
                            return title, parsed_date.strftime("%b %d").upper()
                    except: continue
    except Exception as e:
        print(f"DEBUG: ERROR: {e}")
        
    return up_title, up_date

def update_readme():
    latest_title, latest_link = get_latest_youtube_video()
    up_title, up_date = get_upcoming_video()

    new_table = (
        f"\n| Project Category | Hardware Asset / Title | Status |\n"
        f"| :--- | :--- | :--- |\n"
        f"| **LATEST REPORT** | [{latest_title}]({latest_link}) | `PUBLISHED` |\n"
        f"| **IN TEST BENCH** | {up_title} | `TARGET: {up_date}` |\n"
    )

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    before = content.split(START_TAG)[0]
    after = content.split(END_TAG)[-1]
    final_content = f"{before}{START_TAG}{new_table}{END_TAG}{after}"

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(final_content.strip() + "\n")

if __name__ == "__main__":
    update_readme()
