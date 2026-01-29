import requests
from bs4 import BeautifulSoup
import os

URL = "https://unifafire.edu.br/todasasnoticias/"
STATE_FILE = "last_state.txt"


def get_titles():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    titles = []

    # Seleciona apenas links que realmente parecem notícias
    for link in soup.select("a[href]"):
        href = link.get("href")
        text = link.get_text(strip=True)

        if not href or not text:
            continue

        # Filtro semântico: páginas de notícia
        if "noticia" in href.lower():
            titles.append(text)

    # Remove duplicatas mantendo a ordem
    titles = list(dict.fromkeys(titles))

    return titles


def main():
    current_titles = get_titles()
    current_state = "\n".join(current_titles)

    last_state = ""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            last_state = f.read()

    if current_state != last_state:
        print("🔔 NOVA ATUALIZAÇÃO DETECTADA")
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            f.write(current_state)
    else:
        print("Nenhuma mudança detectada.")


if __name__ == "__main__":
    main()

