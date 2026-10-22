import os
import random
import sqlite3
from datetime import datetime, timedelta, timezone
import re
from html import unescape

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

# override=True: the .env file wins over any old system environment variable.
# (On Render there is no .env file, so Render's Environment tab is used.)
load_dotenv(override=True)

app = Flask(__name__)


@app.context_processor
def inject_today():
    # NASA publishes on US time, so use a US-Eastern-ish "today"
    us_today = datetime.utcnow() - timedelta(hours=5)
    return {"today": us_today.strftime("%Y-%m-%d")}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Strip stray spaces/quotes that often get copied along with the key.
API_KEY = (os.getenv("NASA_API_KEY") or "DEMO_KEY").strip().strip("\"'")

# If you attach a Render persistent disk, set DB_PATH=/var/data/apod.db
DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "apod.db"))

APOD_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic/"
NASA_IMAGES_URL = "https://images-api.nasa.gov/search"
REQUEST_TIMEOUT = 20  # must stay below gunicorn's default 30s worker timeout

SPACE_FACTS = [
    "The Sun contains about 99.8% of the total mass in our Solar System, making it the dominant gravitational force for every planet.",
    "A day on Venus lasts longer than its entire year because the planet rotates extremely slowly while orbiting the Sun relatively quickly.",
    "Jupiter is the largest planet in our Solar System and could fit more than 1,300 Earth-sized planets inside its enormous volume.",
    "Saturn is famous for its spectacular rings, which are made mostly of countless pieces of ice, rock, and dust.",
    "The Moon is slowly moving away from Earth at a rate of about 3.8 centimeters every year due to tidal interactions.",
    "Neutron stars are so dense that a single teaspoon of their material would weigh billions of tons on Earth.",
    "The Milky Way galaxy contains an estimated 100 to 400 billion stars, along with planets, gas, dust, and dark matter.",
    "Light from the Sun takes about 8 minutes and 20 seconds to reach Earth, traveling nearly 300,000 kilometers every second.",
    "The universe is still expanding, a discovery that changed our understanding of cosmology and suggests galaxies continue moving farther apart over time.",
]

SEARCH_MAPPING = {
    "mars": "mars planet",
    "moon": "moon surface",
    "saturn": "saturn planet",
    "jupiter": "jupiter planet",
    "earth": "earth from space",
    "sun": "sun nasa",
    "galaxy": "spiral galaxy",
    "nebula": "nebula",
}


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create the favorites table if it doesn't exist.

    Runs at import time so it also works under gunicorn
    (the `if __name__ == '__main__'` block never runs there).
    """
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL UNIQUE,
            image_url TEXT NOT NULL,
            explanation TEXT,
            media_type TEXT
        )
        """
    )
    conn.commit()
    conn.close()


init_db()

APOD_FALLBACK_URL = "https://science.nasa.gov/wp-json/wp/v2/apod-basic/"




def fetch_apod(selected_date=None, count=None):
    url = "https://science.nasa.gov/wp-json/wp/v2/apod-basic/"

    params = {}

    if count is not None:
        params["count"] = count
    elif selected_date:
        date_code = selected_date.replace("-", "")[2:]
        url = f"{url}{date_code}"

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    # Random count request can return a list
    if isinstance(data, list):
        if not data:
            raise ValueError("NASA returned no APOD images.")

        if count is not None:
            # Keep all returned images available for random selection
            data = random.choice(data)
        else:
            data = data[0]

    if not isinstance(data, dict) or not data.get("date"):
        raise ValueError(f"Invalid NASA response: {str(data)[:300]}")

    print("Requested date:", selected_date or "random/latest")
    print("Returned date:", data.get("date"))
    print("Returned title:", data.get("title"))

    if selected_date and data["date"] != selected_date:
        raise ValueError(
            f"Requested {selected_date}, NASA returned {data['date']}"
        )

    return data


def clean_html(text):
    text = re.sub(r"<br\s*/?>", "\n", text or "", flags=re.IGNORECASE)
    text = re.sub(r"</p\s*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(text).strip()

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/", methods=["GET", "POST"])
def home():
    selected_date = request.args.get("date", "").strip()

    if request.method == "POST":
        selected_date = request.form.get("date", "").strip()

    # NASA APOD starts on 16 June 1995.
    today = datetime.utcnow().date()
    earliest_date = datetime(1995, 6, 16).date()

    if selected_date:
        try:
            requested_date = datetime.strptime(
                selected_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            return "Invalid date. Use YYYY-MM-DD.", 400

        if requested_date < earliest_date:
            return "APOD 16 June 1995 se available hai.", 400

        if requested_date > today:
            return "Future date ki APOD image available nahi hai.", 400

    try:
        data = fetch_apod(selected_date or None)

        returned_date = datetime.strptime(
            data["date"], "%Y-%m-%d"
        ).date()

        # Never silently display a different date.
        if selected_date and data["date"] != selected_date:
            app.logger.error(
                "APOD date mismatch: requested=%s returned=%s",
                selected_date, data["date"]
            )
            return (
                f"Requested date {selected_date}, "
                f"but NASA returned {data['date']}. "
                "Check the Flask terminal logs.",
                502
            )

        previous_date = (
            returned_date - timedelta(days=1)
        ).strftime("%Y-%m-%d") if returned_date > earliest_date else None

        next_date = (
            returned_date + timedelta(days=1)
        ).strftime("%Y-%m-%d") if returned_date < today else None

        media_type = data.get("media_type", "image")

        if media_type == "image":
            image_url = data.get("hdurl") or data.get("url", "")
        else:
            image_url = data.get("url", "")

        explanation = clean_html(data.get("explanation", ""))

        response = app.make_response(render_template(
            "index.html",
            title=data.get("title", "NASA APOD"),
            explanation=explanation,
            image_url=image_url,
            hdurl=image_url,
            media_type=media_type,
            date=data["date"],
            previous_date=previous_date,
            next_date=next_date,
            today=today.strftime("%Y-%m-%d"),
            space_fact=random.choice(SPACE_FACTS),
        ))

        # Avoid serving a previously cached HTML page.
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        return response

    except requests.RequestException:
        app.logger.exception("NASA APOD request failed")
        return "NASA se APOD load nahi hui. Terminal logs check karo.", 502

    except (ValueError, KeyError, TypeError):
        app.logger.exception("APOD response processing failed")
        return "NASA ka response process nahi ho paya. Terminal check karo.", 502








@app.route("/random")
def random_apod():
    try:
        earliest_date = datetime(1995, 6, 16).date()
        today = datetime.now(timezone.utc).date()

        # Random date between APOD launch and today
        days_available = (today - earliest_date).days
        random_days = random.randint(0, days_available)
        random_date = (earliest_date + timedelta(days=random_days)).strftime(
            "%Y-%m-%d"
        )

        data = fetch_apod(selected_date=random_date)

        print(
            "Random APOD selected:",
            data.get("date"),
            "-",
            data.get("title")
        )

        return redirect(f"/?date={data['date']}")

    except (requests.RequestException, ValueError, KeyError, TypeError):
        app.logger.exception("Random APOD failed")
        return "Random APOD load nahi hua. Terminal check karo.", 502



@app.route("/favorite", methods=["POST"])
def favorite():
    title = request.form.get("title", "").strip()
    date = request.form.get("date", "").strip()
    image_url = request.form.get("image_url", "").strip()

    if not title or not date or not image_url:
        return redirect("/favorites")

    item = {
        "title": title,
        "date": date,
        "image_url": image_url,
        "explanation": request.form.get("explanation", ""),
        "media_type": request.form.get("media_type", "image"),
    }

    conn = get_db()
    conn.execute(
        """
        INSERT OR IGNORE INTO favorites
        (title, date, image_url, explanation, media_type)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            item["title"],
            item["date"],
            item["image_url"],
            item["explanation"],
            item["media_type"],
        ),
    )
    conn.commit()
    conn.close()

    return redirect(f"/?date={item['date']}")


@app.route("/favorites")
def favorites():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, title, date, image_url, explanation, media_type FROM favorites"
    ).fetchall()
    conn.close()

    favorites_list = [
        {
            "id": row[0],
            "title": row[1],
            "date": row[2],
            "image_url": row[3],
            "explanation": row[4],
            "media_type": row[5],
        }
        for row in rows
    ]

    return render_template(
        "favorites.html",
        favorites=favorites_list,
        space_fact=random.choice(SPACE_FACTS),
    )


@app.route("/delete_favorite/<date>")
def delete_favorite(date):
    conn = get_db()
    conn.execute("DELETE FROM favorites WHERE date = ?", (date,))
    conn.commit()
    conn.close()

    return redirect("/favorites")


@app.route("/search")
def search():
    keyword = request.args.get("keyword", "").strip().lower()

    if not keyword:
        return redirect("/")

    query = SEARCH_MAPPING.get(keyword, keyword)
    results = []

    try:
        response = requests.get(
            NASA_IMAGES_URL,
            params={"q": query, "media_type": "image"},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        items = response.json().get("collection", {}).get("items", [])

        for item in items[:10]:
            try:
                results.append(
                    {
                        "title": item["data"][0]["title"],
                        "image": item["links"][0]["href"],
                    }
                )
            except (KeyError, IndexError, TypeError):
                continue

    except (requests.RequestException, ValueError) as e:
        print("NASA image search failed:", repr(e))

    return render_template("search_results.html", keyword=keyword, results=results)


@app.route("/jwst")
def jwst():
    jwst_images = [
        {"title": "Pillars of Creation", "image": "/static/jwst/pillars.jpg"},
        {"title": "Cartwheel Galaxy", "image": "/static/jwst/cartwheel.jpg"},
        {"title": "Southern Ring Nebula", "image": "/static/jwst/southern_ring.jpg"},
        {"title": "Stephan's Quintet", "image": "/static/jwst/stephans.jpg"},
        {"title": "Phantom Galaxy", "image": "/static/jwst/phantom.jpg"},
        {"title": "Messier 64 (Webb + Hubble)", "image": "/static/jwst/Messier64.jpg"},
        {"title": "Messier 58", "image": "/static/jwst/Messier58.jpg"},
        {"title": "Messier 77 (MIRI + NIRCam)", "image": "/static/jwst/Messier77.jpg"},
        {"title": "Westerlund 2 (Chandra + Webb)", "image": "/static/jwst/Westerlund2.jpg"},
        {"title": "Jupiter and Europa", "image": "/static/jwst/img1.jpg"},
        {"title": "The Bubble Nebula", "image": "/static/jwst/img2.jpg"},
        {"title": "Hubble mosaic of the majestic Sombrero Galaxy", "image": "/static/jwst/img3.jpg"},
        {"title": "Saturn Portrait by Hubble", "image": "/static/jwst/img4.jpg"},
        {"title": "Latest Saturn Portrait by JWST", "image": "/static/jwst/saturnJWST.png"},
    ]

    return render_template("jwst.html", images=jwst_images)


@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == "__main__":
    # Local development only. On Render, gunicorn runs the app instead.
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "1")