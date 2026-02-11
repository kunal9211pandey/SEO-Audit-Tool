import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Set
import asyncio


class NavigationCrawler:
    # Crawler that identifies and crawls links from the main navigation menu.
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SEOAuditBot/1.0)"
        }
    
    async def crawl_navigation(self, start_url: str) -> List[Dict]:
        # Crawl all links found in the main navigation of the website.Returns a list of page data dictionaries.
        
        # Parse the base domain
        parsed_start = urlparse(start_url)
        base_domain = f"{parsed_start.scheme}://{parsed_start.netloc}"
        
        # Fetch homepage
        homepage_html = await self._fetch_page(start_url)
        if not homepage_html:
            return []
        
        # Extract navigation links
        nav_links = self._extract_navigation_links(homepage_html, base_domain)
        
        # Always include the homepage
        nav_links.add(start_url)
        
        # Crawl each navigation link
        pages_data = []
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            tasks = [self._crawl_page(client, url, base_domain) for url in nav_links]
            pages_data = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_pages = [page for page in pages_data if isinstance(page, dict)]
        
        return valid_pages
    
    async def _fetch_page(self, url: str) -> str:
        # Fetch HTML content of a page.
        try:
            async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None
    
    def _extract_navigation_links(self, html: str, base_url: str) -> Set[str]:
        # Extract links from the main navigation menu.
        soup = BeautifulSoup(html, 'lxml')
        nav_links = set()
        
        # Strategy 1: Find <nav> tags
        nav_elements = soup.find_all('nav')
        
        # Strategy 2: Find header elements
        if not nav_elements:
            nav_elements = soup.find_all('header')
        
        # Strategy 3: Find elements with navigation-related classes/IDs
        if not nav_elements:
            nav_elements = soup.find_all(
                ['div', 'ul'], 
                class_=lambda x: x and any(
                    nav_term in str(x).lower() 
                    for nav_term in ['nav', 'menu', 'header']
                )
            )
        
        # Strategy 4: If still nothing, take the first <ul> in the document
        if not nav_elements:
            first_ul = soup.find('ul')
            if first_ul:
                nav_elements = [first_ul]
        
        # Extract all links from identified navigation elements
        for nav_element in nav_elements:
            for link in nav_element.find_all('a', href=True):
                href = link['href']
                
                # Convert relative to absolute URL
                absolute_url = urljoin(base_url, href)
                
                # Only include same-domain links
                if self._is_same_domain(absolute_url, base_url):
                    # Clean the URL (remove fragments)
                    clean_url = absolute_url.split('#')[0]
                    if clean_url:
                        nav_links.add(clean_url)
        
        return nav_links
    
    def _is_same_domain(self, url: str, base_url: str) -> bool:
        # Check if URL belongs to the same domain as base_url.
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)
        
        return parsed_url.netloc == parsed_base.netloc
    
    async def _crawl_page(self, client: httpx.AsyncClient, url: str, base_domain: str) -> Dict:
        # Crawl a single page and collect data for SEO analysis.
        try:
            response = await client.get(url)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Count internal links
            internal_links = 0
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                if self._is_same_domain(absolute_url, base_domain):
                    internal_links += 1
            
            # Calculate page size
            page_size_kb = len(response.content) / 1024
            
            return {
                "url": url,
                "status_code": response.status_code,
                "html": response.text,
                "headers": dict(response.headers),
                "page_size_kb": round(page_size_kb, 2),
                "internal_links": internal_links
            }
            
        except Exception as e:
            print(f"Error crawling {url}: {e}")
            return {
                "url": url,
                "status_code": 0,
                "html": "",
                "headers": {},
                "page_size_kb": 0,
                "internal_links": 0,
                "error": str(e)
            }
