import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
from time import time
HEADERS = {"User-Agent": "Mozilla/5.0"} 

def get_movie_links_from_page(page: int) -> List[Dict[str, str]]:
    """
    input: page number
    output: list of dictionaries with movie title and url

    description:
        1. Download the page with the best movies.
        2. Find all movie links and return them as a list of dictionaries.
    """
    # step 1.
    links = []
    if page > 9:
        raise ValueError("Page number must be less than 10")

    if page == 0 or page == 1:
        url = "https://www.csfd.cz/zebricky/filmy/nejlepsi/"
    else:
        url = f"https://www.csfd.cz/zebricky/filmy/nejlepsi/?from={page * 100}"

    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error acces page -> {page}: {e}")
        return []
    
    # step 2.
    for article in soup.find_all("article"):
        a_tag = article.find("a")
        if a_tag and a_tag.get("title") and a_tag.get("href"):
            title = a_tag.get("title").strip()
            href = a_tag.get("href").strip()
            full_url = f"https://www.csfd.cz{href}"
            links.append({"title": title, "url": full_url})

    return links

def get_actors_from_detail(title: str, url: str) -> Dict[str, List[str]]:
    """
    input: title of the movie and url
    output: dictionary with movie title as key and list of actors as value

    description:
        1. Download the detail page of the movie.
        2. Find the section with actors and return their names.
    """
    # step 1.
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f" {title}: Error -> {e}")
        return {title: []}
    
    # step 2.
    creators = soup.find("div", class_="creators")
    if not creators:
        print(f"{title}: Missing section 'creators'")
        return {title: []}

    for div in creators.find_all("div"):
        heading = div.find("h4")
        if heading and "Hrají" in heading.get_text():
            actor_links = div.find_all("a")
            actors = [a.get_text(strip=True) for a in actor_links if a.get("href", "").startswith("/tvurce/")]
            return {title: actors}

    return {title: []}

def extract_all_data(pages: int, seq: bool) -> Dict[str, Dict[str, List[str]]]:
    """
    input: number of pages to scrape
    output: dictionary with movie title as key and list of actors as value

    description:
        1. Gather all movie links and afterwards sequentially.
        2. Then download the details of each movie in parallel. -> time consuming
    """
    # step 1.
    all_links = [] 
    pages += 1 # to acces all pages from 1 to pages
    for page in range(1, pages):
        links = get_movie_links_from_page(page)
        all_links.extend(links)

    output = {}
    start = time()
    # step 2.
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [ executor.submit(get_actors_from_detail, film["title"], film["url"]) for film in all_links ]
        for future in as_completed(futures):
            result = future.result()
            output.update(result)
    end = start - time()
    print(f"Parallel scraping took {abs(end):.2f} seconds")

    if seq:
        start = time()
        [get_actors_from_detail( film["title"], film["url"]) for film in all_links]
        end = start - time()
        print(f"Sequential scraping took {abs(end):.2f} seconds")

    return output
