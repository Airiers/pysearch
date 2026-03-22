from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
from ddgs import DDGS

import requests
import feedparser
import re
import spacy
import httpx

def slice_result(result):
    MAX_LEN = 50
    result = result.strip()
    if len(result) > MAX_LEN:
        cut = result[:MAX_LEN]
        cut = cut.rsplit(" ", 1)[0]
        result = cut + "..."
    return result

async def scrap_async(q):
    url = f"https://html.duckduckgo.com/html/?q={q}"
    headers = {"User-Agent": "Mozilla/5.0"}

    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(url, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    result_list = []

    for r in soup.select("div.result"):
        title_tag = r.select_one("a.result__a")
        desc_tag = r.select_one("a.result__snippet")

        if not title_tag:
            continue

        title = title_tag.text.strip()
        link = title_tag["href"]


        if "duckduckgo.com/l/" in link:
            try:
                parsed = urlparse(link)
                link = unquote(parse_qs(parsed.query)["uddg"][0])
            except (KeyError, IndexError):
                continue

        description = desc_tag.text.strip() if desc_tag else ""
        domain = urlparse(link).netloc

        logo = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        fulltitle = title
        result_list.append([slice_result(title), link, description, logo, fulltitle])

    return result_list

def get_image(article):
    image_url = None
    # Cas 1 : enclosure
    if "enclosures" in article and article.enclosures:
        for enclosure in article.enclosures:
            if enclosure.type.startswith("image"):
                image_url = enclosure.href
                break

    # Cas 2 : media_content (fallback)
    if not image_url and "media_content" in article:
        image_url = article.media_content[0].get("url")

    # Cas 3 : description HTML
    if not image_url and "description" in article:
        soup = BeautifulSoup(article.description, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            image_url = img_tag["src"]

    if not image_url:
        image_url = 'https://placehold.net/400x400.png'

    return image_url

stopwords = {
    "être","avoir","faire","dire","aller",
    "probablement","encore","déjà","fini",
    "autour","contre","avec","sans"
}
nlp = spacy.load("fr_core_news_sm", disable=["parser","ner","textcat"])

from functools import lru_cache

@lru_cache(maxsize=500)

def expand(title):
    # enlever citations et ponctuation forte
    title = re.sub(r"«.*?»", "", title)
    title = title.replace("Actualités :", "").replace("Actualité :", "")
    doc = nlp(title)

    keywords = []

    for token in doc:
        if (
            token.pos_ in ["PROPN","NOUN"]  # noms propres ou noms
            and token.lemma_.lower() not in stopwords
            and len(token.text) > 2
        ):
            keywords.append(token.text)

    return " ".join(keywords[:5])

def get_results(articles):
    rss = []
    for article in articles:
        image_url = get_image(article)
        article.fulltitle = article.title
        rss.append([slice_result(article.title), article.link, article.fulltitle, image_url])
    return rss

def bdm_rss():
    response = requests.get("https://www.blogdumoderateur.com/feed/", timeout=3)
    feed = feedparser.parse(response.content)

    tech_articles = [
        entry for entry in feed.entries
        if any(tag.term in ["Tech", "Web"] for tag in entry.tags)
    ]
    return get_results(tech_articles)

def citron_rss():
    response = requests.get("https://www.presse-citron.net/feed/", timeout=3)
    feed = feedparser.parse(response.content)

    tech_articles = [
        entry for entry in feed.entries
        if any(tag.term in ["Sciences", "Test", "Intelligence Artificielle", "Cybersécurité", "Internet", "Gaming"] for tag in entry.tags)
    ]
    return get_results(tech_articles)

def korben_rss():
    response = requests.get("https://korben.info/feed", timeout=3)
    feed = feedparser.parse(response.content)

    tech_articles = [
        entry for entry in feed.entries
        if any(tag.term in ["IA", "intelligence-artificielle/ia-developpement", "scraping", "Python", "open source", "HTML", "developpement/web-developpement", "intelligence-artificielle/actualites-ia"] for tag in entry.tags)
    ]
    return get_results(tech_articles)

def begeek_rss():
    response = requests.get("https://www.begeek.fr/feed", timeout=3)
    feed = feedparser.parse(response.content)

    tech_articles = [
        entry for entry in feed.entries
        if any(tag.term in ["IA", "Tech"] for tag in entry.tags)
    ]
    return get_results(tech_articles)

def ud_rss():
    response = requests.get("https://www.usine-digitale.fr/arc/outboundfeeds/rss/", timeout=3)
    feed = feedparser.parse(response.content)
    tech_articles = [
        entry for entry in feed.entries
        if any(tag.term in ["IA", "Tech", "Cybersécurité", "Meta", "OpenAI"] for tag in entry.tags)
    ]
    return get_results(tech_articles)

def num_ia_rss():
    response = requests.get("https://www.lesnumeriques.com/intelligence-artificielle/rss.xml", timeout=3)
    feed = feedparser.parse(response.content)
    tech_articles = [
        entry for entry in feed.entries
    ]
    return get_results(tech_articles)
def images(q):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.images(
            q,
            max_results=100,
            safesearch="off",
            region="fr-fr"
        ):
            results.append(r["image"])
    return results

def google_news(q):
    response = requests.get(
        f"https://news.google.com/rss/search?q={q.replace(' ','+')}&hl=fr&gl=FR&ceid=FR:fr", timeout=3
    )
    feed = feedparser.parse(response.content)

    results = []

    for e in feed.entries[:20]:
        domain = urlparse(e.source.href).netloc.replace("www.", "")
        logo = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        results.append([
            slice_result(e.title),
            e.link,
            e.title,
            e.published,
            logo,
            ""
        ])

    return results