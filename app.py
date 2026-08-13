import sqlite3
import random
from flask import Flask, render_template, request, redirect
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = "EWqIN1vhaBmFaOeq2RL3wP5CKbIKBrYBWKYSNhIG"

SPACE_FACTS = [
    "The Sun contains about 99.8% of the total mass in our Solar System, making it the dominant gravitational force for every planet.",
    "A day on Venus lasts longer than its entire year because the planet rotates extremely slowly while orbiting the Sun relatively quickly.",
    "Jupiter is the largest planet in our Solar System and could fit more than 1,300 Earth-sized planets inside its enormous volume.",
    "Saturn is famous for its spectacular rings, which are made mostly of countless pieces of ice, rock, and dust.",
    "The Moon is slowly moving away from Earth at a rate of about 3.8 centimeters every year due to tidal interactions.",
    "Neutron stars are so dense that a single teaspoon of their material would weigh billions of tons on Earth.",
    "The Milky Way galaxy contains an estimated 100 to 400 billion stars, along with planets, gas, dust, and dark matter.",
    "Light from the Sun takes about 8 minutes and 20 seconds to reach Earth, traveling nearly 300,000 kilometers every second.",
    "The universe is still expanding, a discovery that changed our understanding of cosmology and suggests galaxies continue moving farther apart over time."
]

SEARCH_MAPPING = {

    "mars":"mars planet",
    "moon":"moon surface",
    "saturn":"saturn planet",
    "jupiter":"jupiter planet",
    "earth":"earth from space",
    "sun":"sun nasa",
    "galaxy":"spiral galaxy",
    "nebula":"nebula"
}

@app.route('/', methods=['GET', 'POST'])
def home():

    selected_date = request.args.get('date', '')

    if request.method == 'POST':
        selected_date = request.form.get('date')

    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"

    if selected_date:
        url += f"&date={selected_date}"

    response = requests.get(url, timeout=30)
    print("URL:", url)
    print("Status:", response.status_code)

    if response.status_code != 200:
        return f"NASA API Error: {response.status_code}<br>{response.text}"

    try:
        data = response.json()
    except Exception:
        return f"Invalid JSON received:<br>{response.text}"

    current_date = datetime.strptime(data["date"], "%Y-%m-%d")
    previous_date = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
    next_date = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")
    random_fact = random.choice(SPACE_FACTS)
    
    return render_template(
        "index.html",
        title=data["title"],
        explanation=data["explanation"],
        image_url=data["url"],
        hdurl=data.get("hdurl", data.get("url")),
        media_type=data["media_type"],
        date=data["date"],
        previous_date=previous_date,
        next_date=next_date,
        space_fact=random_fact
    )

## Random APODs

@app.route('/random')
def random_apod():

    start_date = datetime(1995, 6, 16)
    end_date = datetime.today()

    random_days = random.randint(
        0,
        (end_date - start_date).days
    )

    random_date = (
        start_date + timedelta(days=random_days)
    ).strftime("%Y-%m-%d")

    return redirect(f"/?date={random_date}")

## Add to favorites

@app.route('/favorite', methods=['POST'])
def favorite():

    item = {
        "title": request.form["title"],
        "date": request.form["date"],
        "image_url": request.form["image_url"],
        "explanation": request.form["explanation"],
        "media_type": request.form["media_type"]
    }

    conn = sqlite3.connect("apod.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM favorites WHERE date = ?",
        (item["date"],)
    )

    existing = cursor.fetchone()

    if existing is None:

        cursor.execute(
            """
            INSERT INTO favorites
            (title, date, image_url, explanation, media_type)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                item["title"],
                item["date"],
                item["image_url"],
                item["explanation"],
                item["media_type"]
            )
        )

    conn.commit()
    conn.close()

    date = request.form["date"]
    return redirect(f"/?date={date}")

## Favorites

@app.route('/favorites')
def favorites():

    conn = sqlite3.connect("apod.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM favorites")
    favorites = cursor.fetchall()
    conn.close()

    favorites_list = []

    for row in favorites:

        favorites_list.append({

            "id": row[0],
            "title": row[1],
            "date": row[2],
            "image_url": row[3],
            "explanation": row[4],
            "media_type": row[5]
        })

    space_fact = random.choice(SPACE_FACTS)

    return render_template(
        "favorites.html",
        favorites=favorites_list,
        space_fact=space_fact
    )

## Detele from favprites

@app.route('/delete_favorite/<date>')
def delete_favorite(date):

    conn = sqlite3.connect("apod.db")
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM favorites WHERE date = ?",
        (date,)
    )

    conn.commit()
    conn.close()

    return redirect("/favorites")

## Search route

@app.route('/search')
def search():

    keyword = request.args.get("keyword", "").lower()
    query = SEARCH_MAPPING.get(keyword, keyword)
    url = f"https://images-api.nasa.gov/search?q={query}&media_type=image"

    response = requests.get(url)
    data = response.json()
    results = []

    items = data["collection"]["items"]
    for item in items[:10]:

        try:
            title = item["data"][0]["title"]
            image = item["links"][0]["href"]
            results.append({
                "title": title,
                "image": image
            })

        except:
            continue

    return render_template(
        "search_results.html",
        keyword=keyword,
        results=results
    )

## Telescope gallery

@app.route('/jwst')
def jwst():

    jwst_images = [
        {
            "title": "Pillars of Creation",
            "image": "/static/jwst/pillars.jpg"
        },

        {
            "title": "Cartwheel Galaxy",
            "image": "/static/jwst/cartwheel.jpg"
        },

        {
            "title": "Southern Ring Nebula",
            "image": "/static/jwst/southern_ring.jpg"
        },

        {
            "title": "Stephan's Quintet",
            "image": "/static/jwst/stephans.jpg"
        },

        {
            "title": "Phantom Galaxy",
            "image": "/static/jwst/phantom.jpg"
        },

        {
            "title": "Messier 64 (Webb + Hubble)",
            "image": "/static/jwst/Messier64.jpg"
        },

        {
            "title": "Messier 58",
            "image": "/static/jwst/Messier58.jpg"
        },

        {
            "title": "Messier 77 (MIRI + NIRCam)",
            "image": "/static/jwst/Messier77.jpg"
        },

        {
            "title": "Westerlund 2 (Chandra + Webb)",
            "image": "/static/jwst/Westerlund2.jpg"
        },

        {
            "title": "Jupiter and Europa",
            "image": "/static/jwst/img1.jpg"
        },

        {
            "title": "The Bubble Nebula",
            "image": "/static/jwst/img2.jpg"
        },

        {
            "title": "Hubble mosaic of the majestic Sombrero Galaxy",
            "image": "/static/jwst/img3.jpg"
        },

        {
            "title": "Saturn Portrait by hubble",
            "image": "/static/jwst/img4.jpg"
        },

        {
            "title": "lastest saturn Portrait by JWST",
            "image": "/static/jwst/saturnJWST.png"
        },

    ]

    return render_template(
        "jwst.html",
        images=jwst_images
    )

@app.route('/about')
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)