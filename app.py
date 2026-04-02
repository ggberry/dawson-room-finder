import json
import os
import re
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import dateutil.parser

app = Flask(__name__)

CACHE_FILE = 'timetable_cache.json'
# Supported source HTML files (checked in order of preference)
SOURCE_FILES = [
    'timetable.html'
]

# Only accept room codes in the Dawson format: -1H.4, 4P.04, 3D.23, 1G.18-1, etc.
ROOM_REGEX = re.compile(r'^-?\d+[A-Za-z]+\.\d+(-\d+)?$')


def parse_time_range(time_str):
    """Parse a time string like '11:30 AM - 1:00 PM' into (start, end) time objects."""
    parts = time_str.split('-')
    if len(parts) != 2:
        return None, None
    try:
        start = dateutil.parser.parse(parts[0].strip()).time()
        end = dateutil.parser.parse(parts[1].strip()).time()
        return start, end
    except Exception:
        return None, None


def extract_schedule_from_html(html_content):
    """
    Parse the Dawson timetable HTML by targeting the structured
    <table class="schedule-details"> elements that contain exact
    <td data-label="Day">, <td data-label="Time">, <td data-label="Room"> columns.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    courses = []
    seen = set()

    schedule_tables = soup.find_all('table', class_='schedule-details')

    for table in schedule_tables:
        rows = table.find_all('tr')
        for row in rows:
            day_td = row.find('td', attrs={'data-label': 'Day'})
            time_td = row.find('td', attrs={'data-label': 'Time'})
            room_td = row.find('td', attrs={'data-label': 'Room'})

            if not day_td or not time_td or not room_td:
                continue

            day = day_td.get_text(strip=True)
            time_text = time_td.get_text(strip=True)
            room = room_td.get_text(strip=True)

            if not day or not time_text or not room:
                continue

            # Skip entries where the "room" isn't a valid Dawson room code
            if not ROOM_REGEX.match(room):
                continue

            start_t, end_t = parse_time_range(time_text)
            if not start_t or not end_t:
                continue

            start_str = start_t.strftime('%I:%M %p')
            end_str = end_t.strftime('%I:%M %p')

            key = (room, day, start_str, end_str)
            if key not in seen:
                seen.add(key)
                courses.append({
                    'room': room,
                    'day': day,
                    'start': start_str,
                    'end': end_str
                })

    return courses


def load_courses():
    """Load courses from cache or parse the best available HTML source file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(base_dir, CACHE_FILE)

    # Find available source files and pick the newest one
    best_source = None
    best_mtime = 0
    for fname in SOURCE_FILES:
        fpath = os.path.join(base_dir, fname)
        if os.path.exists(fpath):
            mtime = os.path.getmtime(fpath)
            if mtime > best_mtime:
                best_mtime = mtime
                best_source = fpath

    # Check if cache is still valid
    if os.path.exists(cache_path):
        if best_source is None or os.path.getmtime(cache_path) >= best_mtime:
            with open(cache_path, 'r') as f:
                return json.load(f)

    if best_source is None:
        return None

    print(f"[*] Parsing: {os.path.basename(best_source)}")
    with open(best_source, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    courses = extract_schedule_from_html(html)

    with open(cache_path, 'w') as f:
        json.dump(courses, f, indent=2)

    return courses


def is_class_active(course, check_dt):
    """Check if a course is active at the given datetime."""
    days_map = {
        'monday': 0, 'tuesday': 1, 'wednesday': 2,
        'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
    }

    class_day = days_map.get(course['day'].strip().lower())
    if class_day is None or class_day != check_dt.weekday():
        return False

    try:
        start_t = dateutil.parser.parse(course['start']).time()
        end_t = dateutil.parser.parse(course['end']).time()
    except Exception:
        return False

    current_time = check_dt.time()
    return start_t <= current_time <= end_t


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/check-rooms', methods=['POST'])
def check_rooms():
    data = request.get_json() or {}
    time_str = data.get('datetime', '')

    if time_str:
        try:
            check_dt = dateutil.parser.parse(time_str)
        except Exception:
            return jsonify({'error': 'Invalid datetime format'}), 400
    else:
        check_dt = datetime.now()

    courses = load_courses()

    if courses is None:
        return jsonify({'error': "No timetable HTML file found. Save the Dawson timetable page as 'timetable.html' in the app folder."}), 404

    if len(courses) == 0:
        return jsonify({'error': 'No courses were parsed from the HTML.'}), 500

    all_rooms = sorted(set(c['room'] for c in courses))

    occupied_rooms = set()
    occupied_details = {}

    for c in courses:
        if is_class_active(c, check_dt):
            occupied_rooms.add(c['room'])
            if c['room'] not in occupied_details:
                occupied_details[c['room']] = []
            occupied_details[c['room']].append({
                'day': c['day'],
                'start': c['start'],
                'end': c['end']
            })

    empty_rooms = sorted(set(all_rooms) - occupied_rooms)

    return jsonify({
        'check_time': check_dt.strftime('%A, %Y-%m-%d %H:%M'),
        'total_rooms': len(all_rooms),
        'occupied': {
            'count': len(occupied_rooms),
            'rooms': sorted(list(occupied_rooms)),
            'details': occupied_details
        },
        'empty': {
            'count': len(empty_rooms),
            'rooms': empty_rooms
        }
    })


@app.route('/api/stats', methods=['GET'])
def stats():
    """Return basic stats about the parsed data."""
    courses = load_courses()
    if courses is None:
        return jsonify({'error': 'No data loaded'}), 404

    all_rooms = sorted(set(c['room'] for c in courses))
    all_days = sorted(set(c['day'] for c in courses))

    return jsonify({
        'total_courses': len(courses),
        'total_rooms': len(all_rooms),
        'days': all_days,
        'rooms': all_rooms
    })


if __name__ == '__main__':
    # Delete old cache so a fresh parse happens with the new parser
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CACHE_FILE)
    if os.path.exists(cache_path):
        os.remove(cache_path)
        print("[*] Deleted old cache to force re-parse with fixed parser.")

    print("=" * 50)
    print("  Dawson Classroom Finder")
    print("=" * 50)

    app.run(debug=True, port=5000)
    # gunicorn app:app --bind 0.0.0.0:$PORT
