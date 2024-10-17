from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx
from bs4 import BeautifulSoup
from typing import List

app = FastAPI(title="Simple Web Scraper API")

class ScrapeRequest(BaseModel):
    url: HttpUrl

class ScrapeResponse(BaseModel):
    url: str
    content: str

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(request: ScrapeRequest):
    try:
        # Fetch the web page
        async with httpx.AsyncClient() as client:
            response = await client.get(str(request.url), timeout=10)
        response.raise_for_status()

        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract text content
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
        content = '\n'.join(paragraphs)

        return ScrapeResponse(
            url=str(request.url),
            content=content
        )

    except (httpx.RequestError, httpx.HTTPStatusError) as exc:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {exc}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3426)  # Change port here
