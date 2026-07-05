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

@app.route('/jwst')
def jwst():

    jwst_images = [

        {
            "title": "Cosmic Cliffs",
            "image": "/static/jwst/cosmic_cliffs.jpg",
            "description":"Captured by the James Webb Space Telescope in July 2022, this image reveals a star-forming region in the Carina Nebula. The towering clouds of gas and dust resemble cosmic mountains and are located about 7,600 light-years from Earth. Webb's infrared instruments uncovered details previously hidden from view."
        },

        {
            "title": "Pillars of Creation",
            "image": "/static/jwst/pillars.jpg",
            "description":"Released in October 2022, Webb captured this iconic region inside the Eagle Nebula. These giant pillars of gas and dust are stellar nurseries where new stars are continuously forming. The image showcases Webb's ability to peer through thick interstellar dust using infrared light."
        },

        {
            "title": "Cartwheel Galaxy",
            "image": "/static/jwst/cartwheel.jpg",
            "description":"Observed by JWST in 2022, the Cartwheel Galaxy lies approximately 500 million light-years away in the Sculptor constellation. Its unusual ring-like structure was created by a collision with another galaxy. Webb revealed unprecedented details of star formation within the galaxy."
        },

        {
            "title": "Southern Ring Nebula",
            "image": "/static/jwst/southern_ring.jpg",
            "description":"Released in July 2022, this planetary nebula is located about 2,500 light-years from Earth. It was formed when a dying star expelled its outer layers into space. Webb's observations uncovered a faint companion star hidden within the nebula."
        },

        {
            "title": "Stephan's Quintet",
            "image": "/static/jwst/stephans.jpg",
            "description":"This spectacular image, released in July 2022, depicts five galaxies appearing close together in the constellation Pegasus. Four of the galaxies are gravitationally interacting, triggering bursts of star formation. It is one of the largest images ever produced by JWST."
        },

        {
            "title": "Phantom Galaxy",
            "image": "/static/jwst/phantom.jpg",
            "description":"Captured by JWST in 2022, the Phantom Galaxy (M74) is located about 32 million light-years away in the constellation Pisces. Its well-defined spiral arms contain regions of active star formation. Webb's infrared capabilities revealed intricate structures of gas and dust throughout the galaxy."
        },

        {
            "title": "Messier 64 (Webb + Hubble)",
            "image": "/static/jwst/Messier64.jpg",
            "description":"Messier 64, also known as the Black Eye Galaxy, is a spiral galaxy located about 17 million light-years away in the constellation Coma Berenices. It is famous for its prominent dark dust band near its bright core, giving it the appearance of a black eye. JWST observations provide detailed views of its dust structures and regions of active star formation."
        },

        {
            "title": "Messier 58",
            "image": "/static/jwst/Messier58.jpg",
            "description":"Messier 58 is a barred spiral galaxy situated approximately 62 million light-years from Earth in the Virgo Cluster. It was discovered by Charles Messier in 1779 and is one of the brightest galaxies in the cluster. High-resolution observations reveal intricate spiral arms, interstellar dust, and young star-forming regions."
        },

        {
            "title": "Messier 77 (MIRI + NIRCam)",
            "image": "/static/jwst/Messier77.jpg",
            "description":"Messier 77 is an active spiral galaxy located about 47 million light-years away in the constellation Cetus. It hosts a supermassive black hole at its center, making it one of the best-studied Seyfert galaxies. Infrared observations help astronomers peer through thick dust clouds surrounding its energetic nucleus."
        },

        {
            "title": "Westerlund 2 (Chandra + Webb)",
            "image": "/static/jwst/Westerlund2.jpg",
            "description":"Westerlund 2 is a young and massive star cluster located roughly 20,000 light-years from Earth in the constellation Carina. It contains some of the hottest, brightest, and most massive stars known. Infrared images reveal newborn stars and glowing gas clouds hidden behind dense cosmic dust."
        },

        {
            "title": "Jupiter and Europa",
            "image": "/static/jwst/img1.jpg",
            "description":"This latest image of Jupiter, taken by the NASA/ESA Hubble Space Telescope on 25 August 2020, was captured when the planet was 653 million kilometres from Earth. Hubble’s sharp view is giving researchers an updated weather report on the monster planet’s turbulent atmosphere, including a remarkable new storm brewing, and a cousin of the Great Red Spot changing colour — again. The new image also features Jupiter’s icy moon Europa."
        },

        {
            "title": "The Bubble Nebula",
            "image": "/static/jwst/img2.jpg",
            "description":"The Bubble Nebula, also known as NGC 7635, is an emission nebula located 8 000 light-years away. This stunning new image was observed by the NASA/ESA Hubble Space Telescope to celebrate its 26th year in space."
        },

        {
            "title": "Hubble mosaic of the majestic Sombrero Galaxy",
            "image": "/static/jwst/img3.jpg",
            "description":"NASA/ESA Hubble Space Telescope has trained its razor-sharp eye on one of the universe's most stately and photogenic galaxies, the Sombrero galaxy, Messier 104 (M104). The galaxy's hallmark is a brilliant white, bulbous core encircled by the thick dust lanes comprising the spiral structure of the galaxy. As seen from Earth, the galaxy is tilted nearly edge-on. We view it from just six degrees north of its equatorial plane. This brilliant galaxy was named the Sombrero because of its resemblance to the broad rim and high-topped Mexican hat."
        },

        {
            "title": "Saturn Portrait by hubble",
            "image": "/static/jwst/img4.jpg",
            "description":"The NASA/ESA Hubble Space Telescope’s Wide Field Camera 3 observed Saturn on 20 June 2019 as the planet made its closest approach to Earth this year, at approximately 1.36 billion kilometres away."
        },

        {
            "title": "lastest saturn Portrait by JWST",
            "image": "/static/jwst/saturnJWST.png",
            "description":"Webb teamed up with NASA’s Hubble Space Telescope, observing the ringed planet in complementary wavelengths of light to give us a richer, more layered understanding of its atmosphere. The Hubble image is available in the feature linked below."
        },

        {
            "title": "(Webb + Hubble, Side-by-side)",
            "image": "/static/jwst/hubbWebb.png",
            "description":"Webb teamed up with NASA’s Hubble Space Telescope, observing Saturn in complementary wavelengths of light to give us a richer, more layered understanding of its atmosphere. These images were each captured in 2024, just 14 weeks apart from each other."
        },

    ]

    return render_template(
        "jwst.html",
        images=jwst_images
    )



if __name__ == '__main__':
    app.run(debug=True)