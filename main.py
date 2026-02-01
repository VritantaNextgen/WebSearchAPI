import logging
from fastapi import FastAPI, Query
from duckduckgo_search import DDGS
from itertools import islice

# Setup logging to debug Render's connectivity
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Verified Search API")

def get_results(keywords, max_results=10):
    """
    Attempts to fetch results using different backends if the primary one fails.
    """
    # 2026 Strategy: 'lite' is the most stable for cloud hosting
    backends = ["lite", "html", "api"]
    
    for b in backends:
        try:
            logger.info(f"Trying backend: {b}")
            with DDGS() as ddgs:
                # Use the 'lite' or 'html' backends which are less likely to trigger bot detection
                results = list(islice(ddgs.text(
                    keywords, 
                    region="wt-wt", 
                    safesearch="moderate", 
                    backend=b
                ), max_results))
                
                if results:
                    return results
        except Exception as e:
            logger.error(f"Backend {b} failed: {e}")
            continue
    return []

@app.get("/")
def home():
    return {"status": "active", "endpoint": "/search?q=query"}

@app.get("/search")
async def search(q: str = Query(..., min_length=1)):
    data = get_results(q)
    
    if not data:
        return {
            "query": q,
            "error": "Blocked by provider",
            "suggestion": "Render IP might be rate-limited. Try again in 1 minute.",
            "results": []
        }
    
    return {
        "query": q,
        "count": len(data),
        "results": data
    }
