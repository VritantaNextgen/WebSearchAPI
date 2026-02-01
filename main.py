import logging
from fastapi import FastAPI, Query, HTTPException
from duckduckgo_search import DDGS
from itertools import islice

# Setup logging to see errors in Render logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Resilient Search API")

def fetch_results(query, max_results=10):
    """
    Tries multiple DuckDuckGo backends to ensure results are returned.
    """
    # Order of backends to try: 'lite' and 'html' are usually most stable for servers
    backends = ["lite", "html", "api"]
    
    for backend in backends:
        try:
            logger.info(f"Attempting search with backend: {backend}")
            with DDGS() as ddgs:
                # We use islice to limit results manually if needed
                search_gen = ddgs.text(
                    query, 
                    region='wt-wt', 
                    safesearch='moderate', 
                    backend=backend
                )
                results = list(islice(search_gen, max_results))
                
                if results:
                    logger.info(f"Success with {backend} backend")
                    return results
        except Exception as e:
            logger.warning(f"Backend {backend} failed: {e}")
            continue # Try the next backend
            
    return []

@app.get("/")
def health_check():
    return {"status": "online", "usage": "/search?q=your+query"}

@app.get("/search")
async def search(q: str = Query(..., min_length=1)):
    results = fetch_results(q)
    
    if not results:
        # If all backends fail, return a 404 or a custom message
        return {
            "query": q,
            "status": "no_results_found",
            "message": "Try a different query or wait a moment. The search provider might be rate-limiting.",
            "results": []
        }
        
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
