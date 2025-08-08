import requests
import time
import random
from typing import Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import logger


class HTTPClient:
    """Robust HTTP client with anti-detection and error handling"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0'
    ]
    
    def __init__(self, timeout=10, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a robust session with retry strategy"""
        session = requests.Session()
        
        # Retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate random headers to avoid detection"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none'
        }
    
    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """
        Make a GET request with error handling
        
        Args:
            url: Target URL
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object or None if failed
        """
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 2.0))
            
            headers = self._get_headers()
            headers.update(kwargs.pop('headers', {}))
            
            logger.debug(f"Making request to: {url}")
            
            response = self.session.get(
                url,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True,
                **kwargs
            )
            
            response.raise_for_status()
            logger.debug(f"Successfully fetched: {url} (Status: {response.status_code})")
            
            return response
            
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout for URL: {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning(f"Connection error for URL: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error for URL: {url} - {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception for URL: {url} - {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for URL: {url} - {e}")
            return None
    
    def get_with_security_info(self, url: str) -> Dict[str, Any]:
        """
        Get URL with detailed security information from headers
        
        Args:
            url: Target URL
            
        Returns:
            Dictionary with response and security info
        """
        response = self.get(url)
        
        if not response:
            return {
                'response': None,
                'headers': {},
                'security_headers': {},
                'server_info': {},
                'status': 'failed'
            }
        
        # Extract security-relevant headers
        security_headers = {}
        server_info = {}
        
        headers = response.headers
        
        # Security headers
        security_header_keys = [
            'Content-Security-Policy', 'X-Frame-Options', 'X-XSS-Protection',
            'X-Content-Type-Options', 'Strict-Transport-Security',
            'Referrer-Policy', 'Permissions-Policy', 'Feature-Policy'
        ]
        
        for key in security_header_keys:
            if key in headers:
                security_headers[key] = headers[key]
        
        # Server/WAF identification headers
        server_header_keys = [
            'Server', 'X-Powered-By', 'X-AspNet-Version', 'X-AspNetMvc-Version',
            'X-Drupal-Cache', 'X-Generator', 'X-Varnish', 'X-Cache',
            'CF-Ray', 'CF-Cache-Status', 'X-Akamai-Transformed',
            'X-Served-By', 'X-Timer', 'X-Fastly-Request-ID'
        ]
        
        for key in server_header_keys:
            if key in headers:
                server_info[key] = headers[key]
        
        return {
            'response': response,
            'headers': dict(headers),
            'security_headers': security_headers,
            'server_info': server_info,
            'status': 'success'
        }
    
    def close(self):
        """Close the session"""
        self.session.close()


# Global HTTP client instance
http_client = HTTPClient()