# 🌌 ASTRO-VISION

**Cosmic Daily** is a web app that shows NASA's **Astronomy Picture of the Day (APOD)**. Every day, NASA publishes one image or video of our universe with a short explanation written by a professional astronomer. This app lets you view today's picture, browse the archive by date, and read the story behind each image in a clean full-screen layout.

---

## ✨ Features

- 🖼️ **Picture of the day** shown large, with its title, date and full explanation
- 📅 **Date picker** to open the APOD for any past day in the archive
- ⬅️➡️ **Previous / next day** buttons for quick browsing
- 🎲 **Random picture** button for surprise discoveries
- 🔍 **HD view** to open the high-resolution version of an image
- 🎬 **Video support:** when the daily item is a video, it plays inside the page instead of breaking the layout
- ©️ **Credit line** showing the photographer or institution when one is given
- ⏳ **Loading and error states** that explain what went wrong
- 📱 **Responsive design** for phone, tablet and desktop

---

## 🧰 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, Flask, Requests |
| Frontend | HTML5, CSS3, JavaScript, Jinja2 templates |
| Data | NASA APOD API |

---

## 🔌 API

The app uses NASA's Astronomy Picture of the Day API, which returns a JSON object for a given day.

| Field | Meaning |
|-------|---------|
| `date` | The day of the picture |
| `title` | Title of the picture |
| `explanation` | Short description by an astronomer |
| `url` | Standard-size image (or video link) |
| `hdurl` | High-resolution image, when available |
| `media_type` | `image` or `video` |
| `copyright` | Credit, when the image is not public domain |

Useful options are `date` for a specific day, `start_date` and `end_date` for a range, and `count` for random pictures.

**Rate limits**

| Key | Limit |
|-----|-------|
| `DEMO_KEY` | 30 requests per hour and 50 per day per IP |
| Personal key | 1,000 requests per hour |

---

## 📂 Project Structure

```text
APOD-Explorer/
│
├── app.py                  # Flask app and routes
├── requirements.txt
├── .gitignore
│
├── templates/
│   ├── base.html           # Shared layout
│   └── index.html          # Main APOD page
│
└── static/
    ├── css/
    │   └── style.css
    └── JS/
        └── script.js
```

Update this tree to match your real files.

---

## 🚀 Getting Started

### 1. Prerequisites

- Python 3.9 or newer
- pip
- A free NASA API key (optional but recommended)

### 2. Download the project

Download or clone the repository, then open a terminal in the project folder.

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, create one containing:

```text
Flask
requests
```

### 5. Get a NASA API key

1. Go to the NASA API portal (api.nasa.gov).
2. Fill in the short signup form with your name and email.
3. Your free key arrives by email.

You can start without one by using `DEMO_KEY`, but its limits are low and can run out quickly.

### 6. Set the API key

The key is read from an environment variable named `NASA_API_KEY`, so it never goes in your code.

```bash
# Windows PowerShell
$env:NASA_API_KEY="your-key-here"

# Windows Command Prompt
set NASA_API_KEY=your-key-here

# macOS / Linux
export NASA_API_KEY="your-key-here"
```

If the variable isn't set, the app should fall back to `DEMO_KEY`.

### 7. Run the app

```bash
python app.py
```

Open `127.0.0.1:5000` in your browser.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| Error 403 | The API key is missing or wrong. Check `NASA_API_KEY` |
| Error 429 | You hit the rate limit. Use your own key, cache results, and slow down |
| Image doesn't load | Try the standard version instead of the HD one, or check your connection |
| Page shows a video instead of a picture | Some days the APOD is a video. The app embeds it automatically |
| A date returns an error | APOD starts on 16 June 1995 and has no future dates |

---

## ⚡ Performance Tips

- Cache each day's response, since past APOD data never changes.
- Request only the date you need, not the whole archive.
- Load the standard image first and fetch the HD one only on request.

---

## 🔐 Security Notes

- Never commit your API key to GitHub.
- Add `venv/` and any `.env` files to `.gitignore`.
- Read keys from environment variables, never from code.

---

## 🔮 Future Improvements

- Favorites list to save pictures you love
- Search the archive by title or keyword
- Gallery view for a range of dates
- Download button for wallpapers
- Light and dark theme toggle
- Share button for the daily picture
- Deploy to a cloud host

---

## 🙏 Acknowledgements

- NASA for the APOD service and its open API
- The astronomers who write each daily explanation
- The photographers and observatories who share their images
- Flask for the web framework

---

## 👤 Author

**VINAY VERMA**

---

⭐ If you like this project, give it a star.
