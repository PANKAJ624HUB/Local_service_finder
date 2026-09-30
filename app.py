import math
import os
import sqlite3

from flask import Flask, g, redirect, render_template, request, url_for

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
BHILAI_LAT = 21.1938
BHILAI_LNG = 81.3509

SEED_PROVIDERS = [
    ("Rajesh Kumar", "Electrician", "9876543210", "Sector 1, Bhilai", 200, 4.5, 5, 21.1938, 81.3509, "9 AM - 7 PM", "Wiring, Fan repair, Light installation"),
    ("Suresh Verma", "Electrician", "9876501111", "Sector 6, Bhilai", 250, 4.3, 8, 21.2098, 81.3502, "8 AM - 8 PM", "House wiring, Switchboard, Inverter"),
    ("Amit Patel", "Electrician", "9876502222", "Supela, Bhilai", 180, 4.1, 4, 21.1850, 81.3420, "9 AM - 6 PM", "Fan repair, Light fitting, MCB"),
    ("Vikram Singh", "Electrician", "9876503333", "Nehru Nagar, Bhilai", 300, 4.7, 12, 21.2160, 81.3780, "8 AM - 7 PM", "Industrial wiring, Panel board"),
    ("Deepak Sahu", "Electrician", "9876504444", "Risali, Bhilai", 220, 4.0, 6, 21.1705, 81.3610, "10 AM - 7 PM", "Wiring, Socket repair, Earthing"),
    ("Ravi Mechanic", "Mechanic", "9876511111", "Power House, Bhilai", 400, 4.4, 7, 21.1910, 81.3290, "9 AM - 8 PM", "Car service, Bike repair, Puncture"),
    ("Manoj Gupta", "Mechanic", "9876512222", "Civic Center, Bhilai", 500, 4.6, 10, 21.2070, 81.3485, "8 AM - 8 PM", "Engine, Brake, AC gas"),
    ("Anil Yadav", "Mechanic", "9876513333", "Smriti Nagar, Bhilai", 350, 4.2, 5, 21.1755, 81.3380, "9 AM - 7 PM", "Two-wheeler, Oil change"),
    ("Gopal Plumbing", "Plumber", "9876521111", "Sector 10, Bhilai", 200, 4.3, 9, 21.2015, 81.3655, "8 AM - 7 PM", "Tap leak, Pipeline, Bathroom fitting"),
    ("Hari Lal", "Plumber", "9876522222", "Khursipar, Bhilai", 150, 4.0, 6, 21.1800, 81.3720, "9 AM - 6 PM", "Drain, Tank, Mixer tap"),
    ("Prakash Dewangan", "Plumber", "9876523333", "Durg Road, Bhilai", 250, 4.5, 11, 21.2140, 81.3400, "8 AM - 8 PM", "New pipeline, Motor, Geyser"),
    ("Neha Laptop Care", "Laptop Repair", "9876531111", "Civic Center, Bhilai", 400, 4.6, 6, 21.2065, 81.3490, "10 AM - 8 PM", "Screen, Keyboard, OS install"),
    ("TechFix Hub", "Laptop Repair", "9876532222", "Sector 5, Bhilai", 350, 4.4, 4, 21.1980, 81.3575, "11 AM - 8 PM", "Motherboard, Battery, Data recovery"),
    ("Cool Air Services", "AC Repair", "9876541111", "Sector 8, Bhilai", 500, 4.5, 8, 21.1888, 81.3550, "9 AM - 7 PM", "Gas filling, Servicing, Installation"),
    ("Arctic Cooling", "AC Repair", "9876542222", "Junwani, Bhilai", 450, 4.2, 5, 21.1650, 81.3350, "9 AM - 6 PM", "Split AC, Window AC, PCB"),
    ("Shankar Carpenter", "Carpenter", "9876551111", "Camp 1, Bhilai", 300, 4.3, 15, 21.1955, 81.3440, "8 AM - 6 PM", "Furniture, Door, Modular work"),
    ("Ramesh Wood Works", "Carpenter", "9876552222", "Sector 2, Bhilai", 280, 4.1, 9, 21.2040, 81.3600, "9 AM - 6 PM", "Kitchen, Wardrobe, Repair"),
]


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            profession TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            price INTEGER NOT NULL,
            rating REAL NOT NULL,
            experience INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            working_hours TEXT NOT NULL,
            services TEXT NOT NULL
        )
        """
    )
    count = db.execute("SELECT COUNT(*) FROM providers").fetchone()[0]
    if count == 0:
        db.executemany(
            """
            INSERT INTO providers (
                name, profession, phone, address, price, rating, experience,
                latitude, longitude, working_hours, services
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            SEED_PROVIDERS,
        )
    db.commit()
    db.close()


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return round(2 * r * math.asin(math.sqrt(a)), 1)


def with_distance(rows):
    providers = []
    for row in rows:
        item = dict(row)
        item["distance_km"] = haversine_km(
            BHILAI_LAT, BHILAI_LNG, item["latitude"], item["longitude"]
        )
        providers.append(item)
    return providers


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/providers")
def providers():
    service = request.args.get("service", "").strip()
    location = request.args.get("location", "").strip()
    query = "SELECT * FROM providers WHERE 1=1"
    params = []
    if service:
        query += " AND profession LIKE ?"
        params.append(f"%{service}%")
    if location:
        query += " AND address LIKE ?"
        params.append(f"%{location}%")
    query += " ORDER BY rating DESC"
    rows = get_db().execute(query, params).fetchall()
    return render_template(
        "providers.html",
        providers=with_distance(rows),
        service=service,
        location=location,
    )


@app.route("/provider/<int:provider_id>")
def provider_detail(provider_id):
    row = get_db().execute("SELECT * FROM providers WHERE id = ?", (provider_id,)).fetchone()
    if row is None:
        return render_template("provider.html", provider=None), 404
    provider = with_distance([row])[0]
    return render_template("provider.html", provider=provider)


@app.route("/add-provider", methods=["GET", "POST"])
def add_provider():
    error = None
    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            profession = request.form["profession"].strip()
            phone = request.form["phone"].strip()
            address = request.form["address"].strip()
            price = int(request.form["price"])
            experience = int(request.form["experience"])
            latitude = float(request.form["latitude"])
            longitude = float(request.form["longitude"])
            if not all([name, profession, phone, address]):
                raise ValueError("All fields are required.")
            get_db().execute(
                """
                INSERT INTO providers (
                    name, profession, phone, address, price, rating, experience,
                    latitude, longitude, working_hours, services
                ) VALUES (?, ?, ?, ?, ?, 4.0, ?, ?, ?, '9 AM - 7 PM', 'As discussed')
                """,
                (name, profession, phone, address, price, experience, latitude, longitude),
            )
            get_db().commit()
            return redirect(url_for("providers", service=profession))
        except (KeyError, ValueError, TypeError):
            error = "Please fill every field with valid values."
    return render_template("add-provider.html", error=error, default_lat=BHILAI_LAT, default_lng=BHILAI_LNG)


@app.route("/api/providers")
def api_providers():
    rows = get_db().execute("SELECT * FROM providers ORDER BY name").fetchall()
    return {"providers": with_distance(rows)}


init_db()

if __name__ == "__main__":
    app.run(debug=True)
