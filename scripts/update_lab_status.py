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
    # Fallbacks if no match is found
    upcoming_title = "Data Analysis"
    upcoming_date = "TBD"
    
    try:
        response = urllib.request.urlopen(CSV_URL)
        lines = response.read().decode('utf-8').splitlines()
        
        # Use DictReader to handle columns by name
        # Note: If your CSV has empty lines at the top, we need to find the header
        start_line = 0
        for i, line in enumerate(lines):
            if "CAMPAIGN" in line and "DATE" in line:
                start_line = i
                break
        
        reader = csv.DictReader(lines[start_line:])
        
        for row in reader:
            title = row.get('CAMPAIGN', '').strip()
            date_str = row.get('DATE', '').strip()
            
            if title and date_str:
                try:
                    # Your CSV format is "27-March". We add the year 2026 to parse it.
                    # We use %B for full month name (March)
                    clean_date = datetime.strptime(f"{date_str}-2026", "%d-%B-%Y")
                    
                    if clean_date > today:
                        upcoming_title = title
                        upcoming_date = clean_date.strftime("%b %d").upper()
                        break # Stop at the first future date found
                except ValueError:
                    # Try fallback if date is "March-27" instead of "27-March"
                    try:
                        clean_date = datetime.strptime(f"{date_str}-2026", "%B-%d-%Y")
                        if clean_date > today:
                            upcoming_title = title
                            upcoming_date = clean_date.strftime("%b %d").upper()
                            break
                    except:
                        continue
    except Exception as e:
        print(f"CSV Parse Error: {e}")
        
    return upcoming_title, upcoming_date

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

    if START_TAG not in content:
        header = "### 🔬 Current Research Focus"
        if header in content:
            parts = content.split(header, 1)
            content = f"{parts[0]}{header}\n\n{START_TAG}\n{END_TAG}\n{parts[1]}"
        else:
            content += f"\n\n### 🔬 Current Research Focus\n\n{START_TAG}\n{END_TAG}\n"

    before = content.split(START_TAG)[0]
    after = content.split(END_TAG)[-1]
    final_content = f"{before}{START_TAG}{new_table}{END_TAG}{after}"

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(final_content.strip() + "\n")

if __name__ == "__main__":
    update_readme()
