import feedparser

def slice_result(result):
    MAX_LEN = 50
    result = result.strip()
    if len(result) > MAX_LEN:
        cut = result[:MAX_LEN]
        cut = cut.rsplit(" ", 1)[0]
        result = cut + "..."
    return result

def google_news(q):
    feed = feedparser.parse(
        f"https://news.google.com/rss/search?q={q}&hl=fr&gl=FR&ceid=FR:fr"
    )

    results = []

    for e in feed.entries[:20]:
        results.append([
            slice_result(e.title),
            e.link,
            e.title,
            e.published,
            ""
        ])

    return results

news = google_news("grafikart")
print(news[0])