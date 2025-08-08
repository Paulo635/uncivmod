import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import logger


class SecurityDetector:
    """Comprehensive security mechanism detection system"""
    
    def __init__(self):
        # Security mechanism signatures
        self.security_signatures = {
            # CAPTCHA Systems
            'reCAPTCHA v2': {
                'scripts': [
                    r'recaptcha/api\.js',
                    r'google\.com/recaptcha',
                    r'gstatic\.com/recaptcha'
                ],
                'elements': [
                    r'g-recaptcha',
                    r'data-sitekey',
                    r'grecaptcha'
                ],
                'classes': ['g-recaptcha', 'recaptcha'],
                'keywords': ['recaptcha', 'i\'m not a robot'],
                'headers': []
            },
            'reCAPTCHA v3': {
                'scripts': [
                    r'recaptcha/api\.js\?render=',
                    r'google\.com/recaptcha.*render',
                    r'grecaptcha\.execute'
                ],
                'elements': [
                    r'grecaptcha\.execute',
                    r'data-action',
                    r'recaptcha.*v3'
                ],
                'classes': [],
                'keywords': ['recaptcha', 'grecaptcha.execute'],
                'headers': []
            },
            'reCAPTCHA Enterprise': {
                'scripts': [
                    r'recaptcha.*enterprise',
                    r'enterprise\.google\.com/recaptcha'
                ],
                'elements': [
                    r'enterprise.*recaptcha'
                ],
                'classes': [],
                'keywords': ['recaptcha enterprise'],
                'headers': []
            },
            'hCaptcha': {
                'scripts': [
                    r'hcaptcha\.com',
                    r'js\.hcaptcha\.com'
                ],
                'elements': [
                    r'h-captcha',
                    r'data-sitekey.*hcaptcha',
                    r'hcaptcha'
                ],
                'classes': ['h-captcha', 'hcaptcha'],
                'keywords': ['hcaptcha'],
                'headers': []
            },
            'Cloudflare Turnstile': {
                'scripts': [
                    r'challenges\.cloudflare\.com',
                    r'turnstile\.js'
                ],
                'elements': [
                    r'cf-turnstile',
                    r'turnstile'
                ],
                'classes': ['cf-turnstile'],
                'keywords': ['turnstile', 'cloudflare challenge'],
                'headers': []
            },
            'FunCaptcha': {
                'scripts': [
                    r'funcaptcha\.com',
                    r'arkoselabs\.com'
                ],
                'elements': [
                    r'funcaptcha',
                    r'arkose'
                ],
                'classes': ['funcaptcha', 'arkose'],
                'keywords': ['funcaptcha', 'arkose'],
                'headers': []
            },
            'KeyCAPTCHA': {
                'scripts': [
                    r'keycaptcha\.com'
                ],
                'elements': [
                    r'keycaptcha'
                ],
                'classes': ['keycaptcha'],
                'keywords': ['keycaptcha'],
                'headers': []
            },
            
            # WAF and CDN Protection
            'Cloudflare': {
                'scripts': [
                    r'cloudflare\.com',
                    r'cf-ray'
                ],
                'elements': [],
                'classes': [],
                'keywords': ['cloudflare', 'checking your browser'],
                'headers': ['cf-ray', 'cf-cache-status', 'cf-request-id', 'server.*cloudflare']
            },
            'Akamai': {
                'scripts': [
                    r'akamai.*',
                    r'edgekey\.net'
                ],
                'elements': [],
                'classes': [],
                'keywords': ['akamai'],
                'headers': ['x-akamai-.*', 'akamai-.*', 'server.*akamai']
            },
            'Imperva': {
                'scripts': [
                    r'imperva\.com',
                    r'incapsula\.com'
                ],
                'elements': [],
                'classes': [],
                'keywords': ['imperva', 'incapsula'],
                'headers': ['x-iinfo', 'x-cdn.*incap']
            },
            'Sucuri': {
                'scripts': [
                    r'sucuri\.net'
                ],
                'elements': [],
                'classes': [],
                'keywords': ['sucuri'],
                'headers': ['x-sucuri-.*', 'server.*sucuri']
            },
            'AWS WAF': {
                'scripts': [],
                'elements': [],
                'classes': [],
                'keywords': ['aws waf', 'request blocked'],
                'headers': ['x-amzn-.*', 'x-aws-.*']
            },
            'MaxCDN': {
                'scripts': [
                    r'maxcdn\.com'
                ],
                'elements': [],
                'classes': [],
                'keywords': ['maxcdn'],
                'headers': ['x-cache.*maxcdn']
            },
            'Fastly': {
                'scripts': [],
                'elements': [],
                'classes': [],
                'keywords': ['fastly'],
                'headers': ['x-served-by.*fastly', 'x-cache.*fastly', 'x-timer']
            },
            
            # Bot Detection
            'PerimeterX': {
                'scripts': [
                    r'perimeterx\.net',
                    r'pxchk\.net'
                ],
                'elements': [
                    r'_px'
                ],
                'classes': [],
                'keywords': ['perimeterx'],
                'headers': []
            },
            'DataDome': {
                'scripts': [
                    r'datadome\.co'
                ],
                'elements': [
                    r'datadome'
                ],
                'classes': [],
                'keywords': ['datadome'],
                'headers': ['x-dd-.*']
            },
            'Distil Networks': {
                'scripts': [
                    r'distilnetworks\.com'
                ],
                'elements': [],
                'classes': [],
                'keywords': ['distil networks'],
                'headers': ['x-distil-.*']
            },
            
            # Rate Limiting
            'Rate Limiting': {
                'scripts': [],
                'elements': [],
                'classes': [],
                'keywords': ['rate limit', 'too many requests', 'slow down'],
                'headers': ['x-ratelimit-.*', 'retry-after']
            },
            
            # Other Security
            'ModSecurity': {
                'scripts': [],
                'elements': [],
                'classes': [],
                'keywords': ['mod_security', 'modsecurity'],
                'headers': []
            },
            'Web Application Firewall': {
                'scripts': [],
                'elements': [],
                'classes': [],
                'keywords': ['web application firewall', 'waf', 'blocked by firewall'],
                'headers': []
            }
        }
    
    def detect_security_mechanisms(self, html_content: str, headers: Dict[str, str], url: str = '') -> List[Dict[str, Any]]:
        """
        Detect security mechanisms in HTML content and headers
        
        Args:
            html_content: HTML content to analyze
            headers: HTTP response headers
            url: Source URL for context
            
        Returns:
            List of detected security mechanisms with evidence
        """
        detected_security = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            html_text = html_content.lower()
            headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
            
            logger.debug(f"Analyzing security mechanisms for: {url}")
            
            for security_name, signatures in self.security_signatures.items():
                evidence = []
                
                # Check script sources
                for script_pattern in signatures.get('scripts', []):
                    if self._find_script_evidence(soup, script_pattern):
                        evidence.append(f"Script: {script_pattern}")
                
                # Check HTML elements
                for element_pattern in signatures.get('elements', []):
                    if self._find_element_evidence(soup, element_pattern):
                        evidence.append(f"Element: {element_pattern}")
                
                # Check CSS classes
                for class_pattern in signatures.get('classes', []):
                    if self._find_class_evidence(soup, class_pattern):
                        evidence.append(f"CSS Class: {class_pattern}")
                
                # Check keywords in text
                for keyword in signatures.get('keywords', []):
                    if keyword.lower() in html_text:
                        evidence.append(f"Keyword: {keyword}")
                
                # Check headers
                for header_pattern in signatures.get('headers', []):
                    if self._find_header_evidence(headers_lower, header_pattern):
                        evidence.append(f"Header: {header_pattern}")
                
                # If evidence found, add to detected security
                if evidence:
                    detected_security.append({
                        'name': security_name,
                        'evidence': evidence,
                        'confidence': self._calculate_confidence(evidence),
                        'category': self._get_security_category(security_name)
                    })
            
            logger.debug(f"Found {len(detected_security)} security mechanisms")
            return detected_security
            
        except Exception as e:
            logger.error(f"Error detecting security mechanisms: {e}")
            return []
    
    def _find_script_evidence(self, soup: BeautifulSoup, pattern: str) -> bool:
        """Find evidence in script tags"""
        try:
            scripts = soup.find_all('script', src=True)
            for script in scripts:
                src = script.get('src', '').lower()
                if re.search(pattern, src, re.IGNORECASE):
                    return True
            
            # Also check inline scripts
            scripts = soup.find_all('script')
            for script in scripts:
                content = script.get_text().lower()
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            
            return False
        except Exception:
            return False
    
    def _find_element_evidence(self, soup: BeautifulSoup, pattern: str) -> bool:
        """Find evidence in HTML elements"""
        try:
            # Check all attributes
            elements = soup.find_all()
            for element in elements:
                for attr_name, attr_value in element.attrs.items():
                    if isinstance(attr_value, list):
                        attr_value = ' '.join(attr_value)
                    if re.search(pattern, str(attr_value).lower(), re.IGNORECASE):
                        return True
                    if re.search(pattern, attr_name.lower(), re.IGNORECASE):
                        return True
            
            # Check element text content
            if re.search(pattern, soup.get_text().lower(), re.IGNORECASE):
                return True
            
            return False
        except Exception:
            return False
    
    def _find_class_evidence(self, soup: BeautifulSoup, pattern: str) -> bool:
        """Find evidence in CSS classes"""
        try:
            elements = soup.find_all(class_=re.compile(pattern, re.IGNORECASE))
            return len(elements) > 0
        except Exception:
            return False
    
    def _find_header_evidence(self, headers: Dict[str, str], pattern: str) -> bool:
        """Find evidence in HTTP headers"""
        try:
            for header_name, header_value in headers.items():
                if re.search(pattern, header_name, re.IGNORECASE):
                    return True
                if re.search(pattern, header_value, re.IGNORECASE):
                    return True
            return False
        except Exception:
            return False
    
    def _calculate_confidence(self, evidence: List[str]) -> str:
        """Calculate confidence level based on evidence"""
        evidence_count = len(evidence)
        
        if evidence_count >= 3:
            return 'high'
        elif evidence_count == 2:
            return 'medium'
        else:
            return 'low'
    
    def _get_security_category(self, security_name: str) -> str:
        """Get category for security mechanism"""
        captcha_systems = [
            'reCAPTCHA v2', 'reCAPTCHA v3', 'reCAPTCHA Enterprise',
            'hCaptcha', 'Cloudflare Turnstile', 'FunCaptcha', 'KeyCAPTCHA'
        ]
        
        waf_systems = [
            'Cloudflare', 'Akamai', 'Imperva', 'Sucuri', 'AWS WAF',
            'MaxCDN', 'Fastly', 'ModSecurity', 'Web Application Firewall'
        ]
        
        bot_detection = [
            'PerimeterX', 'DataDome', 'Distil Networks'
        ]
        
        if security_name in captcha_systems:
            return 'captcha'
        elif security_name in waf_systems:
            return 'waf'
        elif security_name in bot_detection:
            return 'bot_detection'
        elif security_name == 'Rate Limiting':
            return 'rate_limiting'
        else:
            return 'other'
    
    def get_security_summary(self, detected_security: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of detected security mechanisms
        
        Args:
            detected_security: List of detected security mechanisms
            
        Returns:
            Summary dictionary
        """
        if not detected_security:
            return {
                'total_mechanisms': 0,
                'mechanism_names': [],
                'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
                'categories': {
                    'captcha': 0,
                    'waf': 0,
                    'bot_detection': 0,
                    'rate_limiting': 0,
                    'other': 0
                }
            }
        
        mechanism_names = [sec['name'] for sec in detected_security]
        confidence_dist = {'high': 0, 'medium': 0, 'low': 0}
        categories = {
            'captcha': 0,
            'waf': 0,
            'bot_detection': 0,
            'rate_limiting': 0,
            'other': 0
        }
        
        for security in detected_security:
            confidence = security.get('confidence', 'low')
            confidence_dist[confidence] = confidence_dist.get(confidence, 0) + 1
            
            category = security.get('category', 'other')
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_mechanisms': len(detected_security),
            'mechanism_names': mechanism_names,
            'confidence_distribution': confidence_dist,
            'categories': categories
        }
    
    def check_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Check for security-related HTTP headers
        
        Args:
            headers: HTTP response headers
            
        Returns:
            Dictionary with security header analysis
        """
        security_headers = {
            'Content-Security-Policy': headers.get('Content-Security-Policy'),
            'X-Frame-Options': headers.get('X-Frame-Options'),
            'X-XSS-Protection': headers.get('X-XSS-Protection'),
            'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
            'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
            'Referrer-Policy': headers.get('Referrer-Policy'),
            'Permissions-Policy': headers.get('Permissions-Policy'),
            'Feature-Policy': headers.get('Feature-Policy')
        }
        
        # Count present headers
        present_headers = {k: v for k, v in security_headers.items() if v is not None}
        
        return {
            'total_security_headers': len(present_headers),
            'present_headers': present_headers,
            'missing_headers': [k for k, v in security_headers.items() if v is None],
            'security_score': len(present_headers) / len(security_headers) * 100
        }