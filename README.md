# Local Service Finder

Search a service, pick a local provider, see price and map, then call them.

## Stack

- Frontend: HTML, CSS, JavaScript, Bootstrap
- Backend: Python + Flask
- Database: SQLite
- Map: Leaflet.js + OpenStreetMap

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Flow

Home → search (e.g. Electrician) → provider list → provider details → map + Call Now.

## Demo data

17 providers in Bhilai: Electrician, Mechanic, Plumber, Laptop Repair, AC Repair, Carpenter.

No login, payments, chat, or booking.
