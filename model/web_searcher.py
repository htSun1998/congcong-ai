import requests
from bs4 import BeautifulSoup


class WebSearcher:
    def __init__(self) -> None:
        self.url = 'https://www.bing.com/search?q={q}&count=10'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5023.114 Safari/537.36",
        }

    def search(self, q: str):
        url = self.url.format(q=q)
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        search_results = []
        for result in soup.find_all('li', class_='b_algo'):
            try:
                title = result.find('a').text
                url = result.find('a')['href']
                snippet = result.find('p').text
                search_results.append({
                    'title': title,
                    'url': url,
                    'snippet': snippet
                })
            except:
                continue
        return self.parse_response(search_results)

    def parse_response(self, raw_response):
        response = []
        for r in raw_response:
            response.append({
                "id": "",
                "datasetId": "",
                "collectionId": "",
                "sourceName": "link:" + r["url"],
                "q": r["title"],
                "a": r["snippet"]
            })
        return response
