from bs4 import BeautifulSoup
from typing import Dict, List


class SEOAnalyzer:
    # Analyzes crawled pages for technical SEO issues.
    # SEO best practice thresholds
    MIN_TITLE_LENGTH = 30
    MAX_TITLE_LENGTH = 60
    MIN_META_DESC_LENGTH = 120
    MAX_META_DESC_LENGTH = 160
    
    def analyze_page(self, page_data: Dict) -> Dict:
        # Perform SEO analysis on a single page.
        # Returns a dictionary with SEO metrics and detected issues.
        url = page_data.get("url", "")
        status_code = page_data.get("status_code", 0)
        html = page_data.get("html", "")
        
        if not html or status_code != 200:
            return {
                "url": url,
                "status_code": status_code,
                "title_length": 0,
                "meta_description_length": 0,
                "h1_count": 0,
                "canonical_present": False,
                "noindex": False,
                "page_size_kb": page_data.get("page_size_kb", 0),
                "internal_links": page_data.get("internal_links", 0),
                "issues": ["PAGE_NOT_ACCESSIBLE"] if status_code != 200 else ["NO_HTML_CONTENT"]
            }
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Extract SEO elements
        title = self._extract_title(soup)
        meta_description = self._extract_meta_description(soup)
        h1_tags = soup.find_all('h1')
        canonical = soup.find('link', rel='canonical')
        noindex = self._check_noindex(soup)
        
        # Calculate metrics
        title_length = len(title) if title else 0
        meta_desc_length = len(meta_description) if meta_description else 0
        h1_count = len(h1_tags)
        canonical_present = canonical is not None
        
        # Detect issues
        issues = self._detect_issues(
            title_length=title_length,
            meta_desc_length=meta_desc_length,
            h1_count=h1_count,
            canonical_present=canonical_present,
            noindex=noindex,
            status_code=status_code
        )
        
        return {
            "url": url,
            "status_code": status_code,
            "title": title,
            "title_length": title_length,
            "meta_description": meta_description,
            "meta_description_length": meta_desc_length,
            "h1_count": h1_count,
            "h1_tags": [h1.get_text(strip=True) for h1 in h1_tags],
            "canonical_present": canonical_present,
            "canonical_url": canonical.get('href') if canonical else None,
            "noindex": noindex,
            "page_size_kb": page_data.get("page_size_kb", 0),
            "internal_links": page_data.get("internal_links", 0),
            "issues": issues
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc:
            meta_desc = soup.find('meta', attrs={'property': 'og:description'})
        return meta_desc.get('content', '').strip() if meta_desc else ""
    
    def _check_noindex(self, soup: BeautifulSoup) -> bool:
        """Check if page has noindex directive."""
        robots_meta = soup.find('meta', attrs={'name': 'robots'})
        if robots_meta:
            content = robots_meta.get('content', '').lower()
            if 'noindex' in content:
                return True
        return False
    
    def _detect_issues(
        self, 
        title_length: int, 
        meta_desc_length: int, 
        h1_count: int,
        canonical_present: bool,
        noindex: bool,
        status_code: int
    ) -> List[str]:
        
        # Detect SEO issues based on metrics.
        issues = []
        
        # Title checks
        if title_length == 0:
            issues.append("MISSING_TITLE")
        elif title_length < self.MIN_TITLE_LENGTH:
            issues.append("TITLE_TOO_SHORT")
        elif title_length > self.MAX_TITLE_LENGTH:
            issues.append("TITLE_TOO_LONG")
        
        # Meta description checks
        if meta_desc_length == 0:
            issues.append("MISSING_META_DESCRIPTION")
        elif meta_desc_length < self.MIN_META_DESC_LENGTH:
            issues.append("META_DESCRIPTION_TOO_SHORT")
        elif meta_desc_length > self.MAX_META_DESC_LENGTH:
            issues.append("META_DESCRIPTION_TOO_LONG")
        
        # H1 checks
        if h1_count == 0:
            issues.append("MISSING_H1")
        elif h1_count > 1:
            issues.append("MULTIPLE_H1_TAGS")
        
        # Canonical check
        if not canonical_present:
            issues.append("MISSING_CANONICAL")
        
        # Noindex check
        if noindex:
            issues.append("NOINDEX_PRESENT")
        
        # Status code check
        if status_code != 200:
            issues.append(f"HTTP_{status_code}")
        
        return issues
