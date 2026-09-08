import os
from dataclasses import dataclass
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from tavily import TavilyClient

load_dotenv()


@dataclass
class TavilySearchResponse:
    data: list


class TavilyService:
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("Missing TAVILY_API_KEY environment variable")
        self.client = TavilyClient(api_key=api_key)

    def search_companies(self, query: str, num_results: int = 5):
        try:
            response = self.client.search(
                query=f"{query} company pricing",
                max_results=num_results,
                search_depth="advanced",
            )
            results = self._get_results(response)
            data = [
                {
                    "url": r.get("url", ""),
                    "metadata": {"title": r.get("title", "")},
                    "content": r.get("content", ""),
                }
                for r in results
            ]
            return TavilySearchResponse(data=data)
        except Exception as e:
            print(e)
            return TavilySearchResponse(data=[])

    def scrape_company_pages(self, url: str):
        try:
            response = self.client.extract(urls=[url])
            results = response.get("results", [])
            if not results:
                return None
            markdown = results[0].get("raw_content") or results[0].get("content", "")

            @dataclass
            class _Page:
                markdown: str = ""

            return _Page(markdown=markdown or "")
        except Exception as e:
            print(e)
            return None

    def _get_results(self, response):
        results = getattr(response, "results", None)
        if results is not None:
            return results
        if isinstance(response, dict):
            return response.get("results", [])
        return response["results"] if "results" in response else []
