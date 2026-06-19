import json
import random
from flask import Flask, render_template, request, redirect
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = "EWqIN1vhaBmFaOeq2RL3wP5CKbIKBrYBWKYSNhIG"

SPACE_FACTS = [

    "A day on Venus is longer than a year on Venus.",
    "One million Earths could fit inside the Sun.",
    "Light from the Sun takes about 8 minutes to reach Earth.",
    "Saturn could float in water because it is less dense than water.",
    "Olympus Mons on Mars is the largest volcano in the Solar System.",
    "Neutron stars can spin up to 600 times per second.",
    "The footprints on the Moon may last millions of years.",
    "Jupiter has at least 95 known moons.",
    "Mars has the tallest mountain in the Solar System.",
    "The Sun contains 99.86% of the Solar System's mass.",
    "A year on Mercury lasts only 88 Earth days.",
    "A day on Mercury lasts 176 Earth days.",
    "The Milky Way galaxy is about 100,000 light-years wide.",
    "There are billions of galaxies in the observable universe.",
    "The Moon is moving away from Earth by about 3.8 cm each year.",
    "The hottest planet in our Solar System is Venus.",
    "The coldest known place in the universe is the Boomerang Nebula.",
    "Black holes can bend light using gravity.",
    "The International Space Station travels at 28,000 km/h.",
    "The ISS circles Earth about 16 times a day.",
    "A teaspoon of neutron star material would weigh billions of tons.",
    "The largest known star is UY Scuti.",
    "Earth is the only known planet with liquid water on its surface.",
    "The Sun is actually white, not yellow.",
    "Space is completely silent because sound cannot travel in a vacuum.",
    "Jupiter's Great Red Spot is a giant storm.",
    "Pluto takes 248 Earth years to orbit the Sun.",
    "The Andromeda Galaxy is moving toward the Milky Way.",
    "The Milky Way and Andromeda will collide in about 4.5 billion years.",
    "The first human in space was Yuri Gagarin.",
    "The first person on the Moon was Neil Armstrong.",
    "The Moon has moonquakes similar to earthquakes.",
    "Mars has blue sunsets.",
    "The Sun loses millions of tons of mass every second.",
    "Earth travels around the Sun at about 107,000 km/h.",
    "The largest canyon in the Solar System is on Mars.",
    "Some exoplanets rain molten glass.",
    "A light-year is about 9.46 trillion kilometers.",
    "There may be more planets than stars in the Milky Way.",
    "The Moon reflects only about 12% of sunlight.",
    "Venus rotates in the opposite direction of most planets.",
    "The first artificial satellite was Sputnik 1.",
    "Astronauts grow slightly taller in space.",
    "Jupiter protects Earth by attracting many comets and asteroids.",
    "The largest asteroid is Ceres.",
    "The Sun will become a red giant in about 5 billion years.",
    "The universe is estimated to be 13.8 billion years old.",
    "More energy from the Sun reaches Earth in one hour than humanity uses in a year.",
    "The Hubble Space Telescope has made over 1.5 million observations.",
    "There are more stars in the universe than grains of sand on Earth.",
    "A black hole's gravity is so strong that even light cannot escape.",
    "The Moon has no atmosphere.",
    "The largest moon in the Solar System is Ganymede.",
    "Saturn's rings are mostly made of ice.",
    "The closest star to Earth after the Sun is Proxima Centauri.",
    "The first reusable spacecraft was the Space Shuttle.",
    "Mars has two moons: Phobos and Deimos.",
    "The Voyager 1 spacecraft is the farthest human-made object from Earth.",
    "Uranus rotates on its side.",
    "The largest known structure in the universe is the Hercules-Corona Borealis Great Wall."

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

@app.route('/favorite', methods=['POST'])
def favorite():

    item = {
        "title": request.form["title"],
        "date": request.form["date"],
        "image_url": request.form["image_url"],
        "explanation": request.form["explanation"],
        "media_type": request.form["media_type"]
    }

    with open("favorites.json", "r") as f:
        favorites = json.load(f)

    
        already_exists = False

        for fav in favorites:

            if fav["date"] == item["date"]:
                already_exists = True
                break

    if not already_exists:
        favorites.append(item)

    with open("favorites.json", "w") as f:
        json.dump(favorites, f, indent=4)

    date = request.form["date"]
    return redirect(f"/?date={date}")

@app.route('/favorites')
def favorites():

    with open("favorites.json", "r") as f:
        favorites_list = json.load(f)

    return render_template(
        "favorites.html",
        favorites=favorites_list
    )

@app.route('/delete_favorite/<date>')
def delete_favorite(date):

    with open("favorites.json", "r") as f:
        favorites = json.load(f)

    favorites = [
        item for item in favorites
        if item["date"] != date
    ]

    with open("favorites.json", "w") as f:
        json.dump(favorites, f, indent=4)

    return redirect("/favorites")

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



if __name__ == '__main__':
    app.run(debug=True)