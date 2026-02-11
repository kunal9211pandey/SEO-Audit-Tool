from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import asyncio

from crawler import NavigationCrawler
from seo_analyzer import SEOAnalyzer
from database import AuditDatabase

app = FastAPI(title="Technical SEO Audit API")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database
db = AuditDatabase()


class AuditRequest(BaseModel):
    url: HttpUrl


class AuditResponse(BaseModel):
    audit_id: str
    status: str
    message: str


@app.post("/audit", response_model=AuditResponse)
async def start_audit(request: AuditRequest):
    # Start a new SEO audit for the given URL.This will crawl navigation links and perform SEO checks.
    audit_id = str(uuid.uuid4())
    url = str(request.url)
    
    # Initialize audit record
    db.create_audit(audit_id, url)
    
    # Run audit in background
    asyncio.create_task(run_audit(audit_id, url))
    
    return AuditResponse(
        audit_id=audit_id,
        status="started",
        message="Audit started successfully"
    )


async def run_audit(audit_id: str, url: str):
    # Background task to perform the actual audit.
    try:
        # Update status
        db.update_status(audit_id, "crawling")
        
        # Crawl navigation links
        crawler = NavigationCrawler()
        pages = await crawler.crawl_navigation(url)
        
        # Update status
        db.update_status(audit_id, "analyzing")
        
        # Analyze each page for SEO issues
        analyzer = SEOAnalyzer()
        results = []
        
        for page_data in pages:
            analysis = analyzer.analyze_page(page_data)
            results.append(analysis)
        
        # Calculate summary
        summary = calculate_summary(results)
        
        # Save results
        db.save_results(audit_id, {
            "url": url,
            "pages_crawled": len(results),
            "summary": summary,
            "pages": results,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        db.update_status(audit_id, "completed")
        
    except Exception as e:
        db.update_status(audit_id, "failed")
        db.save_error(audit_id, str(e))


def calculate_summary(results: List[Dict]) -> Dict:
    # Calculate summary statistics from page results.
    summary = {
        "missing_title": 0,
        "missing_meta_description": 0,
        "multiple_h1": 0,
        "noindex_pages": 0,
        "non_200_pages": 0
    }
    
    for page in results:
        if page.get("status_code") != 200:
            summary["non_200_pages"] += 1
        if page.get("title_length", 0) == 0:
            summary["missing_title"] += 1
        if page.get("meta_description_length", 0) == 0:
            summary["missing_meta_description"] += 1
        if page.get("h1_count", 0) > 1:
            summary["multiple_h1"] += 1
        if page.get("noindex"):
            summary["noindex_pages"] += 1
    
    return summary


@app.get("/audit/{audit_id}")
async def get_audit_results(audit_id: str):
    # Retrieve audit results by audit ID.
    audit = db.get_audit(audit_id)
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return audit


@app.get("/health")
async def health_check():
    # Health check endpoint.
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
