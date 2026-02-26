from flask import Flask, render_template, request
from scrapper import scrap
from scrapper import bdm_rss
from scrapper import images
from scrapper import google_news


import requests

def get_bing_image():
    api = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=fr-FR"
    data = requests.get(api).json()
    rel_url = data["images"][0]["url"]
    img_url = "https://www.bing.com" + rel_url
    return img_url

app = Flask(__name__)

@app.route("/")
def home():
    image = get_bing_image()
    bdm = bdm_rss()
    return render_template("index.html", image=image, bdm=bdm)
@app.route("/search", methods=["GET"])
def recevoir():
    if request.method == "GET":
        # search = request.form["q"] # ? POST METHOD
        search = request.args.get("q") # ? GET METHOD
        results = scrap(search)
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8042, debug=True)
