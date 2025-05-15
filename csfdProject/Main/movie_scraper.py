import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed


def extract_data(page: int)-> Dict:
    """
    input: None

    Request data from CSFD and extract movie and actors data

    output: Dict{ movie_name : {"actors" : [herci]} }
    """

    # max acces CSFD 
    if page > 9:
        raise ValueError("Page number must be less than 10")
    
    # CSFD links 
    output = {}
    if page == 0 or page == 1:
        url = f"https://www.csfd.cz/zebricky/filmy/nejlepsi/"
    else:
        url = f"https://www.csfd.cz/zebricky/filmy/nejlepsi/?from={page*100}"

    headers = {"User-Agent": "Mozilla/5.0"}

    # Request data 
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")  # nahradíme pevné mezery
    except Exception as e:
        print(f"Nepodarilo se extrahovat data z CSFD -> {e}")
        return

    articles = soup.find_all("article")
    if not articles:
        print("Nenalezen zadny articl")
    
    for article in articles:
        # Each movie has its own article-tag
        try:
            a = article.find("a")
            if a is None:
                continue

            # Get movie name from a-tag nested in article 
            movie_name = a.get("title").strip()
            link = f"https://www.csfd.cz{a.get("href").strip()}"
           

            try:
                response_herec  = requests.get(link, headers=headers)
                soup_herec = BeautifulSoup(response_herec.text , "html.parser")  # nahradíme pevné mezery
            except Exception as e:
                print(f"Nepodarilo se extrahovat data z CSFD -> {e}")
                continue

            main_div = soup_herec.find("div", class_="creators")
            if not main_div:
                print(f"Nepodarilo se extrahovat data hercu pro film -> {movie_name}")
                continue

            divs     = main_div.find_all("div")
            actors   = []
            for div in divs:
                if "Hrají" not in div.find("h4").get_text(strip=True):
                    continue
                else:
                    a_actors = div.find_all("a")
                    actors = [actor.get_text(strip=True) for actor in a_actors if actor.get('href').startswith("/tvurce/")]
                    break

            output[movie_name] =  {"actors" : actors}
            

        except Exception as e:
            print(f"Chyba extrakce z CSFD -> {e}")

    return output

def concurently_extract_data(pages: int = 3) -> Dict:
    output = {}
    with ThreadPoolExecutor(max_workers = 3) as executor:
        """
        concurently extract data d
        """
        future_data = []
        for page in range(1, pages): 
            future_data.append(executor.submit(extract_data, page))

        for future in as_completed(future_data):
            result = future.result()
            output.update(result)

    return output


data = concurently_extract_data(2)
for dat in data:
    print(f"Movie: {dat}")
    print(f"Actors: {data[dat]['actors']}")
    print() 