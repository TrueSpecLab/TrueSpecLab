import csv
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import io

# --- CONFIGURATION ---
CHANNEL_ID = "UChy7QRfWL2mDN8seUqjD8tw" 
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTUahX8lrOmnF4JlJYKzuNVSnZZJAC8UoLhjKcmXRcy0MpRHbieAzLIAqoh9oEL1bgLYBVQuNVFsX1V/pub?gid=270845334&single=true&output=csv" # <--- Put your published CSV link here
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
    except Exception as e:
        return "Latest Video Data Unavailable", "https://youtube.com/@truespeclab"

def get_upcoming_video():
    today = datetime.now()
    current_year = today.year
    upcoming_title = "Data Analysis in Progress"
    upcoming_date_str = "TBD"

    try:
        # Fetch the CSV directly from Google's servers
        req = urllib.request.urlopen(CSV_URL)
        csv_data = req.read().decode('utf-8')
        lines = csv_data.splitlines()
        
        # Dynamically find the header row
        header_idx = 0
        for i, line in enumerate(lines):
            if "TITLE COPY" in line or "CAMPAIGN" in line:
                header_idx = i
                break
                
        reader = csv.DictReader(lines[header_idx:])
        
        for row in reader:
            month = row.get('MONTH', '').strip()
            day = row.get('DAY', '').strip()
            # Try to grab TITLE COPY, fallback to CAMPAIGN if that's where you put it
            title = row.get('TITLE COPY', '').strip()
            if not title:
                title = row.get('CAMPAIGN', '').strip()
            
            if month and day and title:
                try:
                    date_obj = datetime.strptime(f"{current_year} {month} {day}", "%Y %B %d")
                    if date_obj > today:
                        upcoming_title = title
                        upcoming_date_str = date_obj.strftime("%b %d")
                        break
                except ValueError:
                    continue
    except Exception as e:
        print(f"Failed to fetch or parse CSV from Google: {e}")
                
    return upcoming_title, upcoming_date_str

def update_readme():
    latest_title, latest_link = get_latest_youtube_video()
    upcoming_title, upcoming_date_str = get_upcoming_video()

    md_table = f"""| Project Category | Hardware Asset / Title | Status |
| :--- | :--- | :--- |
| **LATEST REPORT** | [{latest_title}]({latest_link}) | `PUBLISHED` |
| **IN TEST BENCH** | {upcoming_title} | `TARGET: {upcoming_date_str.upper()}` |"""

    with open(README_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(
        r'().*?()',
        r'\1\n' + md_table + r'\n\2',
        content,
        flags=re.DOTALL
    )

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == "__main__":
    update_readme()
