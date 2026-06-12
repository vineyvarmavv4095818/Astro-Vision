import json
import random
from flask import Flask, render_template, request, redirect
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

API_KEY = "EWqIN1vhaBmFaOeq2RL3wP5CKbIKBrYBWKYSNhIG"

@app.route('/', methods=['GET', 'POST'])
def home():

    selected_date = request.args.get('date', '')

    if request.method == 'POST':
        selected_date = request.form.get('date')

    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"

    if selected_date:
        url += f"&date={selected_date}"



    # response = requests.get(url)

    # print("URL:", url)
    # print("Status:", response.status_code)
    # print("Response:", response.text)

    # data = response.json()


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
        "image_url": request.form["image_url"]
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

if __name__ == '__main__':
    app.run(debug=True)