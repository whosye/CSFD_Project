import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

HEADERS = {"User-Agent": "Mozilla/5.0"}

# -------------------------------
# Fáze 1 – zisk filmu a odkazu
# -------------------------------
def get_movie_links_from_page(page: int) -> List[Dict[str, str]]:
    links = []
    if page > 9:
        raise ValueError("Maximálně 9 stránek")

    if page == 0 or page == 1:
        url = "https://www.csfd.cz/zebricky/filmy/nejlepsi/"
    else:
        url = f"https://www.csfd.cz/zebricky/filmy/nejlepsi/?from={page * 100}"

    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"❌ Chyba při načítání stránky {page}: {e}")
        return []

    for article in soup.find_all("article"):
        a_tag = article.find("a")
        if a_tag and a_tag.get("title") and a_tag.get("href"):
            title = a_tag.get("title").strip()
            href = a_tag.get("href").strip()
            full_url = f"https://www.csfd.cz{href}"
            links.append({"title": title, "url": full_url})

    return links

# -------------------------------
# Fáze 2 – zisk herců z detailu
# -------------------------------
def get_actors_from_detail(title: str, url: str) -> Dict[str, List[str]]:
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"❌ {title}: Chyba při načítání detailu: {e}")
        return {title: []}

    creators = soup.find("div", class_="creators")
    if not creators:
        print(f"⚠️ {title}: Chybí sekce 'creators'")
        return {title: []}

    for div in creators.find_all("div"):
        heading = div.find("h4")
        if heading and "Hrají" in heading.get_text():
            actor_links = div.find_all("a")
            actors = [a.get_text(strip=True) for a in actor_links if a.get("href", "").startswith("/tvurce/")]
            return {title: actors}

    return {title: []}

# -------------------------------
# Hlavní orchestr
# -------------------------------
def extract_all_data(pages: int = 2) -> Dict[str, Dict[str, List[str]]]:
    all_links = []

    # Fáze 1: získání všech linků (sekvenčně nebo malým paralelismem)
    for page in range(pages):
        links = get_movie_links_from_page(page)
        all_links.extend(links)

    output = {}

    # Fáze 2: paralelní stahování detailních stránek
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(get_actors_from_detail, film["title"], film["url"])
            for film in all_links
        ]
        for future in as_completed(futures):
            result = future.result()
            output.update(result)

    return output

# -------------------------------
# Test: spusť funkci
# -------------------------------
if __name__ == "__main__":
    data = extract_all_data(2)
    for movie, info in data.items():
        print(f"{movie}: {', '.join(info) if info else 'Bez herců'}")
