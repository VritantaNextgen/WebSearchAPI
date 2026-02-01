from fastapi import FastAPI, Query
from duckduckgo_search import DDGS

app = FastAPI(title="DuckDuckGo Search API")

@app.get("/")
def home():
    return {"message": "Welcome to the Search API! Use /search?q=your_query"}

@app.get("/search")
def search(q: str = Query(..., description="The search query")):
    """
    Performs a DuckDuckGo search and returns the top results.
    """
    with DDGS() as ddgs:
        # We limit results to 10 for speed; you can increase this
        results = [r for r in ddgs.text(q, max_results=10)]
    
    return {
        "query": q,
        "results": results
    }
