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
        return "Latest Lab Report", "https://youtube.com/@truespeclab"

def get_upcoming_video():
    today = datetime.now()
    upcoming_title = "Telemetry Analysis"
    upcoming_date = "TBD"

    try:
        response = urllib.request.urlopen(CSV_URL)
        content = response.read().decode('utf-8')
        # Skip the metadata rows in your Google Sheet (Year: 2026, etc.)
        lines = content.splitlines()
        
        # Find the actual header row starting with # or CAMPAIGN
        start_row = 0
        for i, line in enumerate(lines):
            if "CAMPAIGN" in line and "DATE" in line:
                start_row = i
                break
        
        reader = csv.DictReader(lines[start_row:])
        for row in reader:
            raw_date = row.get('DATE', '').strip()
            title = row.get('CAMPAIGN', '').strip()
            
            if raw_date and title:
                # Format in your CSV is "27-March" or "10-April"
                try:
                    # Append current year to the string for parsing
                    clean_date = datetime.strptime(f"{raw_date}-2026", "%d-%B-%Y")
                    if clean_date > today:
                        upcoming_title = title
                        upcoming_date = clean_date.strftime("%b %d").upper()
                        break
                except:
                    continue
    except:
        pass
    return upcoming_title, upcoming_date

def update_readme():
    start_tag = ""
    end_tag = ""
    
    latest_title, latest_link = get_latest_youtube_video()
    up_title, up_date = get_upcoming_video()

    new_table = f"""
| Project Category | Hardware Asset / Title | Status |
| :--- | :--- | :--- |
| **LATEST REPORT** | [{latest_title}]({latest_link}) | `PUBLISHED` |
| **IN TEST BENCH** | {up_title} | `TARGET: {up_date}` |
"""

    with open(README_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    skip = False
    
    # Logic: Copy all lines, but when we hit START, insert the table and skip 
    # everything until we hit END.
    for line in lines:
        if start_tag in line:
            new_lines.append(line)
            new_lines.append(new_table)
            skip = True
        elif end_tag in line:
            new_lines.append(line)
            skip = False
        elif not skip:
            new_lines.append(line)

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    update_readme()
