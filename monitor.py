import requests
from bs4 import BeautifulSoup
import hashlib
import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree


URL = "https://unifafire.edu.br/todasasnoticias/"
STATE_FILE = "last_state.txt"
FEED_FILE = "feed.xml"


def get_news():
    response = requests.get(URL, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.elespare-posts-list-post-items a")

    news = []
    for a in items:
        title = a.get_text(strip=True)
        link = a.get("href")

        if title and link:
            news.append({
                "title": title,
                "link": link
            })

    return news


def calculate_state(news):
    joined = "".join(item["title"] + item["link"] for item in news)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def load_last_state():
    if not os.path.exists(STATE_FILE):
        return ""

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(state)


def generate_feed(news):
    rss = Element("rss", version="2.0")
    channel = SubElement(rss, "channel")

    SubElement(channel, "title").text = "UNIFAFIRE – Notícias e Avisos"
    SubElement(channel, "link").text = URL
    SubElement(channel, "description").text = "Feed automático de atualizações do site da UNIFAFIRE"
    SubElement(channel, "lastBuildDate").text = datetime.utcnow().strftime(
        "%a, %d %b %Y %H:%M:%S GMT"
    )

    for item in news:
        entry = SubElement(channel, "item")
        SubElement(entry, "title").text = item["title"]
        SubElement(entry, "link").text = item["link"]
        SubElement(entry, "guid").text = item["link"]
        SubElement(entry, "pubDate").text = datetime.utcnow().strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )

    ElementTree(rss).write(FEED_FILE, encoding="utf-8", xml_declaration=True)


def main():
    news = get_news()

    if not news:
        print("Nenhuma notícia encontrada.")
        return

    current_state = calculate_state(news)
    last_state = load_last_state()

    if current_state != last_state:
        print("Mudança detectada. Atualizando feed...")
        generate_feed(news)
        save_state(current_state)
    else:
        print("Nenhuma mudança detectada.")


if __name__ == "__main__":
    main()
