import requests
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template, request
from flask_caching import Cache
from scrapper import scrap_async
from scrapper import bdm_rss
from scrapper import citron_rss
from scrapper import korben_rss
from scrapper import begeek_rss
from scrapper import ud_rss
from scrapper import num_ia_rss
from scrapper import images
from scrapper import google_news
from scrapper import expand

sources = [
    bdm_rss,
    citron_rss,
    korben_rss,
    begeek_rss,
    ud_rss,
    num_ia_rss
]

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})

@cache.cached(timeout=3600, key_prefix='bing_image')  # Cache 1 heure
def get_bing_image():
    api = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=fr-FR"
    data = requests.get(api).json()
    rel_url = data["images"][0]["url"]
    img_url = "https://www.bing.com" + rel_url
    return img_url

def scrap_cached(search):
    return scrap_async(search)

@cache.cached(timeout=300, key_prefix='articles') # Cache 5 minutes
def get_all_articles():
    with ThreadPoolExecutor(max_workers=6) as executor:
        results = list(executor.map(lambda source: source(), sources))
    articles = []
    for result in results:
        articles.extend(result)
    return articles


@app.route("/")
def home():
    image = get_bing_image()
    articles = random.sample(get_all_articles(), min(18, len(get_all_articles())))
    return render_template("index.html", image=image, articles=articles)
@app.route("/search", methods=["GET"])
async def recevoir():
    if request.method == "GET":
        # search = request.form["q"] # ? POST METHOD
        search = request.args.get("q") # ? GET METHOD
        results = await scrap_cached(search)
    else:
        results = []
    return render_template("result.html", results=results, value=search)
@app.route("/images", methods=["GET"])
def recevoir_images():
    if request.method == "GET":
        # search = request.form["q"] # ? POST METHOD
        search = request.args.get("q") # ? GET METHOD
        results = images(search)
    else:
        results = []
    return render_template("images.html", results=results, value=search)

@app.route("/actus", methods=["GET"])
def recevoir_actus():
    if request.method == "GET":
        # search = request.form["q"] # ? POST METHOD
        search = request.args.get("q") # ? GET METHOD
        results = google_news(search)
    else:
        results = []
    return render_template("actus.html", results=results, value=search)

@app.route("/sources", methods=["GET"])
def recevoir_sources():
    if request.method == "GET":
        # search = request.form["q"] # ? POST METHOD
        search = request.args.get("q") # ? GET METHOD
        search = expand(search)
        results = google_news(search)
    else:
        results = []
    return render_template("actus.html", results=results, value=search)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8042, debug=True)