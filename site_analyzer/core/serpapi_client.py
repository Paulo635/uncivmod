import requests
import re
from typing import List, Dict, Any
from urllib.parse import urlparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import logger


class SerpApiClient:
    """Client for SerpApi Google search integration"""
    
    def __init__(self, api_key: str = "ff9fd017a23127aba8f396c1873d6648485f46c7f3d1464854e0d5ece8a6012b"):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"
        
        # Patterns to filter out irrelevant URLs
        self.irrelevant_patterns = [
            r'.*\b(docs?|help|support|api|dev|developer|documentation)\.',
            r'.*\b(stackoverflow|github|reddit|wiki|forum|blog)\.',
            r'.*\b(youtube|facebook|twitter|instagram|linkedin)\.',
            r'.*\/(docs?|help|support|api|developer|documentation)\/',
            r'.*\.(pdf|doc|docx|txt|zip|exe)$',
            r'.*\b(terms|privacy|policy|about|contact)\b',
        ]
        
    def search(self, query: str, num_results: int = 20) -> List[Dict[str, Any]]:
        """
        Perform Google search via SerpApi and extract organic results
        
        Args:
            query: Search query
            num_results: Number of results to fetch
            
        Returns:
            List of dictionaries with URL and metadata
        """
        try:
            logger.info(f"Searching SerpApi for: '{query}'")
            
            params = {
                'q': query,
                'api_key': self.api_key,
                'engine': 'google',
                'num': min(num_results, 100),  # SerpApi limit
                'hl': 'en',
                'gl': 'us'
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"SerpApi error: {data['error']}")
                return []
            
            organic_results = data.get('organic_results', [])
            logger.info(f"Found {len(organic_results)} organic results")
            
            # Filter and process results
            filtered_results = []
            for result in organic_results:
                url = result.get('link', '')
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                
                if self._is_relevant_url(url):
                    filtered_results.append({
                        'url': url,
                        'title': title,
                        'snippet': snippet,
                        'domain': self._extract_domain(url)
                    })
                else:
                    logger.debug(f"Filtered out irrelevant URL: {url}")
            
            logger.success(f"Filtered to {len(filtered_results)} relevant URLs")
            return filtered_results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"SerpApi request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in SerpApi search: {e}")
            return []
    
    def _is_relevant_url(self, url: str) -> bool:
        """
        Check if URL is relevant for e-commerce analysis
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is relevant, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
        
        # Check against irrelevant patterns
        for pattern in self.irrelevant_patterns:
            if re.search(pattern, url.lower()):
                return False
        
        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not parsed.netloc or not parsed.scheme:
                return False
            
            # Skip non-web protocols
            if parsed.scheme not in ['http', 'https']:
                return False
                
            return True
            
        except Exception:
            return False
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: Full URL
            
        Returns:
            Domain name
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return url
    
    def get_search_results_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of search results
        
        Args:
            results: List of search results
            
        Returns:
            Summary dictionary
        """
        domains = [result['domain'] for result in results]
        unique_domains = list(set(domains))
        
        return {
            'total_results': len(results),
            'unique_domains': len(unique_domains),
            'domains': unique_domains[:10],  # Top 10 domains
            'sample_urls': [result['url'] for result in results[:5]]  # First 5 URLs
        }