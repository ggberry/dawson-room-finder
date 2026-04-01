import json
import os
import sys
import re
from datetime import datetime
from bs4 import BeautifulSoup
import dateutil.parser

CACHE_FILE = 'timetable_cache.json'
MASTER_FILE = 'dawson_master.html'

def parse_time(time_str):
    try:
         parsed = dateutil.parser.parse(time_str)
         return parsed.time()
    except:
         return None

def is_class_active(day_of_week_str, start_time_str, end_time_str, current_datetime):
    days_map = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1,
        'wednesday': 2, 'wed': 2,
        'thursday': 3, 'thu': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6
    }
    
    class_day = days_map.get(day_of_week_str.strip().lower()[:3])
    if class_day != current_datetime.weekday():
        return False
        
    start_t = parse_time(start_time_str)
    end_t = parse_time(end_time_str)
    
    if not start_t or not end_t:
        return False
        
    current_time = current_datetime.time()
    return start_t <= current_time <= end_t

def extract_schedule_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    courses = []
    
    # Text-based extraction from table rows or generic containers
    rows = soup.find_all(['tr', 'div', 'li']) 
    
    time_regex = re.compile(r'(\d{1,2}[:.]\d{2}(?:\s?[AP]M)?).*?-.*?(\d{1,2}[:.]\d{2}(?:\s?[AP]M)?)')
    room_regex = re.compile(r'\b[1-8][A-Z]\.[1-9][0-9]?\b|\b[A-Z]\d{2,3}\b')
    days_regex = re.compile(r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b', re.IGNORECASE)

    for row in rows:
        text = row.get_text(separator=' ', strip=True)
        
        time_match = time_regex.search(text)
        room_match = room_regex.search(text)
        day_match = days_regex.search(text)
        
        if time_match and room_match:
            start_time = time_match.group(1).replace('.', ':')
            end_time = time_match.group(2).replace('.', ':')
            room = room_match.group(0)
            day = day_match.group(0) if day_match else "Unknown"
            
            course_obj = {
                'room': room,
                'day': day,
                'start': start_time,
                'end': end_time
            }
            if course_obj not in courses:
                courses.append(course_obj)
            
    return courses

def main():
    print("=== Dawson Empty Classroom Finder ===")
    courses = []
    
    if os.path.exists(CACHE_FILE):
        ans = input(f"Found cached parsed data ({CACHE_FILE}). Load it instantly? (y/n): ")
        if ans.lower() == 'y':
            with open(CACHE_FILE, 'r') as f:
                courses = json.load(f)
                
    if not courses:
        print(f"Looking for '{MASTER_FILE}' ...")
        if not os.path.exists(MASTER_FILE):
            print(f"ERROR: Could not find '{MASTER_FILE}'.")
            print("Please run the provided Javascript code in your Opera GX developer console")
            print("to auto-download the file, and then move it to this folder.")
            return

        print(f"Reading {MASTER_FILE} (This might take a second as the file could be massive)...")
        with open(MASTER_FILE, 'r', encoding='utf-8', errors='ignore') as f:
            html = f.read()

        print("Parsing classes from HTML...")
        courses = extract_schedule_from_html(html)
        
        print(f"\nExtracted {len(courses)} valid class schedules. Saving JSON cache...")
        with open(CACHE_FILE, 'w') as f:
            json.dump(courses, f, indent=4)

    if len(courses) == 0:
        print("No classes were found. Exiting.")
        return
        
    # Analyze unique rooms
    all_rooms = set([c['room'] for c in courses if 'room' in c])
    print(f"\nTotal unique rooms found globally: {len(all_rooms)}")
    if len(all_rooms) == 0:
        print("No valid rooms were extracted. The regex parser may need adjustment.")
        return
        
    # Prompt for time
    use_current = input("Check for empty rooms right NOW? (y/n): ")
    if use_current.lower() == 'y':
        now = datetime.now()
    else:
        time_str = input("Enter a time to check (e.g., 2026-04-01 14:30): ")
        now = dateutil.parser.parse(time_str)
        
    print(f"\nAnalyzing emptiness for DateTime: {now.strftime('%A, %Y-%m-%d %H:%M')}")
    
    occupied_rooms = set()
    for c in courses:
        if c.get('day') and c.get('start') and c.get('end'):
            if c['day'].lower() != "unknown" and is_class_active(c['day'], c['start'], c['end'], now):
                occupied_rooms.add(c['room'])
                
    empty_rooms = all_rooms - occupied_rooms
    
    print("\n" + "="*40)
    print(f"Occupied Rooms ({len(occupied_rooms)}):")
    print(", ".join(sorted(list(occupied_rooms))) if occupied_rooms else "None")
    print("="*40)
    print(f"EMPTY ROOMS ({len(empty_rooms)}):")
    print(", ".join(sorted(list(empty_rooms))) if empty_rooms else "None")
    print("="*40)

if __name__ == "__main__":
    main()
