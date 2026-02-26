import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
import feedparser
from ddgs import DDGS

def slice_result(result):
    MAX_LEN = 50
    result = result.strip()
    if len(result) > MAX_LEN:
        cut = result[:MAX_LEN]
        cut = cut.rsplit(" ", 1)[0]
        result = cut + "..."
    return result

def scrap(q):
    url = f"https://duckduckgo.com/html/?q={q}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    result_list = []

    for r in soup.select("div.result"):
        title_tag = r.select_one("a.result__a")
        desc_tag = r.select_one("a.result__snippet")

        if not title_tag:
            continue

        title = title_tag.text.strip()
        link = title_tag["href"]

        # Corrige lien DuckDuckGo
        if "duckduckgo.com/l/" in link:
            parsed = urlparse(link)
            link = unquote(parse_qs(parsed.query)["uddg"][0])

        description = desc_tag.text.strip() if desc_tag else ""

        domain = urlparse(link).netloc
        logo = f"https://icons.duckduckgo.com/ip3/{domain}.ico"
        fulltitle = title
        # LISTE comme tu veux
        result_list.append([slice_result(title), link, description, logo, fulltitle])

    return result_list

def bdm_rss():
    feed = feedparser.parse("https://www.blogdumoderateur.com/feed/")

    tech_articles = [
        entry for entry in feed.entries
        if any(tag.term == "Tech" for tag in entry.tags)
    ]
    rss = []
    for article in tech_articles:

        # Récupération de l'image
        image_url = None

        # Cas 1 : enclosure (le plus fréquent sur BDM)
        if "enclosures" in article and article.enclosures:
            for enclosure in article.enclosures:
                if enclosure.type.startswith("image"):
                    image_url = enclosure.href
                    break

        # Cas 2 : media_content (fallback)
        if not image_url and "media_content" in article:
            image_url = article.media_content[0].get("url")

        if not image_url:
            image_url = 'https://placehold.net/400x400.png'
        article.fulltitle = article.title
        rss.append([slice_result(article.title), article.link, article.fulltitle, image_url])
    return rss

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
    feed = feedparser.parse(
        f"https://news.google.com/rss/search?q={q.replace(' ','+')}&hl=fr&gl=FR&ceid=FR:fr"
    )

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