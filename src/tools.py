from typing import List
import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
from langchain_community.retrievers import TavilySearchAPIRetriever

@tool
def search_tool(query: str) -> List[dict]:
    """Searches the web for a given query using Tavily and returns a list of search results."""
    try:
        retriever = TavilySearchAPIRetriever(k=5)
        results = retriever.invoke(query)
        return [{"url": doc.metadata["source"], "content": doc.page_content} for doc in results]
    except Exception as e:
        # Return an empty list or handle the error as appropriate
        return

@tool
def scrape_tool(url: str) -> str:
    """Scrapes the text content of a given URL."""
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        text = "\n".join(chunk for chunk in (phrase.strip() for line in (line.strip() for line in soup.get_text().splitlines()) for phrase in line.split("  ")) if chunk)
        return text if text else "No content found."
    except requests.RequestException as e:
        return f"Error scraping URL {url}: {e}"