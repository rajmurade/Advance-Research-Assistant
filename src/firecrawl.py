import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


class TavilyService:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("Missing TAVILY_API_KEY environment variable")
        self.client = TavilyClient(api_key=api_key)

    def search_companies(self, query: str, num_results: int = 5):
        try:
            result = self.client.search(
                query=f"{query} company pricing",
                max_results=num_results
            )
            return _SearchResult(result.get("results", []))
        except Exception as e:
            print(e)
            return _SearchResult([])

    def scrape_company_pages(self, url: str):
        try:
            result = self.client.extract(urls=[url])
            results = result.get("results", [])
            if results:
                return _ExtractResult(results[0].get("raw_content", ""))
            return None
        except Exception as e:
            print(e)
            return None


class _SearchResult:
    def __init__(self, results):
        self.data = []
        for item in results:
            self.data.append({
                "url": item.get("url", ""),
                "markdown": item.get("content", ""),
                "metadata": {"title": item.get("title", "Unknown")},
            })


class _ExtractResult:
    def __init__(self, markdown):
        self.markdown = markdown
