import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import xml.etree.ElementTree as ET

URL = "https://unifafire.edu.br/todasasnoticias/"
STATE_FILE = "last_state.txt"
FEED_FILE = "feed.xml"


def get_news():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    news = []

    for link in soup.select("a[href]"):
        href = link.get("href")
        title = link.get_text(strip=True)

        if not href or not title:
            continue

        if "noticia" in href.lower():
            if href.startswith("/"):
                href = "https://unifafire.edu.br" + href

            news.append((title, href))

    # remove duplicatas mantendo ordem
    seen = set()
    unique_news = []
    for item in news:
        if item not in seen:
            seen.add(item)
            unique_news.append(item)

    return unique_news


def load_last_state():
    if not os.path.exists(STATE_FILE):
        return set()

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())


def save_last_state(news):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        for title, link in news:
            f.write(f"{title}|{link}\n")


def load_or_create_feed():
    if not os.path.exists(FEED_FILE):
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")

        ET.SubElement(channel, "title").text = "UNIFAFIRE – Notícias e Avisos"
        ET.SubElement(channel, "link").text = URL
        ET.SubElement(channel, "description").text = (
            "Feed automático de atualizações do site da UNIFAFIRE"
        )

        tree = ET.ElementTree(rss)
        tree.write(FEED_FILE, encoding="utf-8", xml_declaration=True)

    return ET.parse(FEED_FILE)


def add_items_to_feed(tree, new_items):
    channel = tree.getroot().find("channel")

    for title, link in new_items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = title
        ET.SubElement(item, "link").text = link
        ET.SubElement(item, "guid").text = link
        ET.SubElement(item, "pubDate").text = datetime.utcnow().strftime(
            "%a, %d %b %Y %H:%M:%S GMT"
        )


def main():
    current_news = get_news()
    last_state = load_last_state()

    new_items = []
    new_state = set()

    for title, link in current_news:
        key = f"{title}|{link}"
        new_state.add(key)
        if key not in last_state:
            new_items.append((title, link))

    if new_items:
        feed_tree = load_or_create_feed()
        add_items_to_feed(feed_tree, new_items)
        feed_tree.write(FEED_FILE, encoding="utf-8", xml_declaration=True)

        save_last_state(current_news)
        print(f"🔔 {len(new_items)} nova(s) notícia(s) adicionada(s) ao RSS")
    else:
        print("Nenhuma novidade detectada.")


if __name__ == "__main__":
    main()
