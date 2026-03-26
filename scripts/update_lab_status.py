import csv
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import io

# --- CONFIGURATION ---
CHANNEL_ID = "UChy7QRfWL2mDN8seUqjD8tw" 
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUahX8lrOmnF4JlJYKzuNVSnZZJAC8UoLhjKcmXRcy0MpRHbieAzLIAqoh9oEL1bgLYBVQuNVFsX1V/pub?gid=270845334&single=true&output=csv" 
README_PATH = "README.md"

# We use string joining to prevent browsers from hiding the tags during copy-paste
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
        return "Latest Lab Report", "https://youtube.com/truespeclab"

def get_upcoming_video():
    today = datetime.now()
    up_title, up_date = "Data Analysis", "TBD"
    try:
        response = urllib.request.urlopen(CSV_URL)
        lines = response.read().decode('utf-8').splitlines()
        reader = csv.reader(lines)
        
        # Hunt for the header row in your specific Google Sheet
        camp_idx, date_idx = -1, -1
        for row in reader:
            if "CAMPAIGN" in row and "DATE" in row:
                camp_idx, date_idx = row.index("CAMPAIGN"), row.index("DATE")
                continue
            
            if camp_idx != -1 and len(row) > max(camp_idx, date_idx):
                title, d_str = row[camp_idx].strip(), row[date_idx].strip()
                if title and d_str:
                    try:
                        # Parsing "27-March" format
                        c_date = datetime.strptime(f"{d_str}-2026", "%d-%B-%Y")
                        if c_date > today:
                            up_title, up_date = title, c_date.strftime("%b %d").upper()
                            break
                    except: continue
    except: pass
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

    try:
        with open(README_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        content = "### 🔬 Current Research Focus\n\n"

    # If tags are missing, we append them to the end of the focus section
    if START_TAG not in content:
        # Check if the header exists; if so, append after it.
        header = "### 🔬 Current Research Focus"
        if header in content:
            before_h, after_h = content.split(header, 1)
            content = f"{before_h}{header}\n\n{START_TAG}\n{END_TAG}\n{after_h}"
        else:
            content += f"\n\n### 🔬 Current Research Focus\n\n{START_TAG}\n{END_TAG}\n"

    # Surgically replace content between tags
    before = content.split(START_TAG)[0]
    after = content.split(END_TAG)[-1]
    
    final_content = f"{before}{START_TAG}{new_table}{END_TAG}{after}"

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(final_content.strip() + "\n")

if __name__ == "__main__":
    update_readme()
