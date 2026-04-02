# Dawson Classroom Finder

A fast, fully-featured web application that helps students and faculty at Dawson College find empty classrooms in real-time. Whether you are looking for a quiet place to study, a room to collaborate on a group project, or the weekly schedule of a specific room, Dawson Classroom Finder has you covered.

## Features
- **Real-Time Availability:** Fetches the current timetable data to show which rooms are available and which are occupied right now.
- **Future Time Checks:** Want to plan ahead? Use the date/time picker to check room availability at any specific time.
- **Advanced Filtering:** Filter the results by specific floors (e.g. 5, 8, -1) and wings (e.g. A, B, C).
- **Drag-to-Select Filters:** Easily swipe or drag across the filter pills to select multiple floors or wings quickly, perfect for mobile devices.
- **Minimum Duration Filter:** Filter for rooms that are available for a minimum amount of time (e.g. 1 hour, 2 hours).
- **Theming:** Choose from multiple color themes (Default, Ocean Depths, Forest Canopy, Sunset Amber, Midnight).
- **Full Room Schedules:** Click on any room (available or occupied) to view its full schedule for the rest of the week.

## Setup & Running Locally

1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```
2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://localhost:5000` in your web browser.

## Data Source
Room data and schedules are scraped directly from the official Dawson College Timetable tool to ensure high accuracy.

## Contributing
Pull requests, bug reports, and features suggestions are always welcome!
