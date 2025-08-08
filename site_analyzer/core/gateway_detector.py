import re
from typing import List, Dict, Any, Set
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.logger import logger


class GatewayDetector:
    """Comprehensive payment gateway detection system"""
    
    def __init__(self):
        # Payment gateway signatures - scripts, domains, form patterns, etc.
        self.gateway_signatures = {
            # Brazilian Gateways
            'PagSeguro': {
                'scripts': [
                    r'pagseguro\.uol\.com\.br',
                    r'stc\.pagseguro\.uol\.com\.br',
                    r'assets\.pagseguro\.com\.br',
                    r'pagseguro\.js',
                    r'directpayment\.js'
                ],
                'domains': ['pagseguro.uol.com.br', 'stc.pagseguro.uol.com.br'],
                'forms': [r'action.*pagseguro', r'PagSeguroDirectPayment'],
                'classes': ['pagseguro', 'pag-seguro'],
                'keywords': ['pagseguro', 'uol']
            },
            'Mercado Pago': {
                'scripts': [
                    r'secure\.mlstatic\.com',
                    r'mp-public-key',
                    r'mercadopago\.js',
                    r'sdk\.mercadopago\.com'
                ],
                'domains': ['mercadopago.com.br', 'mercadopago.com', 'secure.mlstatic.com'],
                'forms': [r'action.*mercadopago', r'data-preference-id'],
                'classes': ['mercadopago', 'mp-button'],
                'keywords': ['mercadopago', 'mercado pago']
            },
            'Cielo': {
                'scripts': [
                    r'cielo\.com\.br',
                    r'cieloecommerce\.cielo\.com\.br',
                    r'cielo.*checkout',
                    r'cielo\.js'
                ],
                'domains': ['cielo.com.br', 'cieloecommerce.cielo.com.br'],
                'forms': [r'action.*cielo', r'cielo.*form'],
                'classes': ['cielo', 'cielo-checkout'],
                'keywords': ['cielo']
            },
            'Rede': {
                'scripts': [
                    r'userede\.com\.br',
                    r'erede\.com\.br',
                    r'rede.*checkout'
                ],
                'domains': ['userede.com.br', 'erede.com.br'],
                'forms': [r'action.*rede', r'rede.*form'],
                'classes': ['rede', 'erede'],
                'keywords': ['rede', 'e-rede']
            },
            'GetNet': {
                'scripts': [
                    r'getnet\.com\.br',
                    r'checkout.*getnet',
                    r'getnet.*js'
                ],
                'domains': ['getnet.com.br'],
                'forms': [r'action.*getnet'],
                'classes': ['getnet'],
                'keywords': ['getnet']
            },
            'Yapay': {
                'scripts': [
                    r'yapay\.com\.br',
                    r'checkout.*yapay'
                ],
                'domains': ['yapay.com.br'],
                'forms': [r'action.*yapay'],
                'classes': ['yapay'],
                'keywords': ['yapay']
            },
            'Pagar.me': {
                'scripts': [
                    r'pagar\.me',
                    r'pagarme\.js',
                    r'assets\.pagar\.me'
                ],
                'domains': ['pagar.me', 'assets.pagar.me'],
                'forms': [r'action.*pagar\.me'],
                'classes': ['pagarme'],
                'keywords': ['pagar.me', 'pagarme']
            },
            'Boleto Bancário': {
                'scripts': [
                    r'boleto',
                    r'itau.*boleto',
                    r'bradesco.*boleto',
                    r'bb.*boleto'
                ],
                'domains': [],
                'forms': [r'boleto', r'banking.*slip'],
                'classes': ['boleto', 'bank-slip'],
                'keywords': ['boleto bancário', 'boleto', 'banking slip']
            },
            
            # International Gateways
            'PayPal': {
                'scripts': [
                    r'paypal\.com',
                    r'paypalobjects\.com',
                    r'paypal\.me',
                    r'paypal.*checkout',
                    r'paypal.*button'
                ],
                'domains': ['paypal.com', 'paypalobjects.com'],
                'forms': [r'action.*paypal', r'data-paypal'],
                'classes': ['paypal', 'paypal-button'],
                'keywords': ['paypal']
            },
            'Stripe': {
                'scripts': [
                    r'stripe\.com',
                    r'js\.stripe\.com',
                    r'stripe.*checkout',
                    r'stripe.*elements'
                ],
                'domains': ['stripe.com', 'js.stripe.com'],
                'forms': [r'action.*stripe', r'data-stripe'],
                'classes': ['stripe', 'stripe-button'],
                'keywords': ['stripe']
            },
            'Square': {
                'scripts': [
                    r'squareup\.com',
                    r'square.*checkout',
                    r'square.*js'
                ],
                'domains': ['squareup.com'],
                'forms': [r'action.*square'],
                'classes': ['square', 'square-button'],
                'keywords': ['square', 'squareup']
            },
            'Adyen': {
                'scripts': [
                    r'adyen\.com',
                    r'checkoutshopper.*adyen',
                    r'adyen.*checkout'
                ],
                'domains': ['adyen.com'],
                'forms': [r'action.*adyen'],
                'classes': ['adyen'],
                'keywords': ['adyen']
            },
            'Braintree': {
                'scripts': [
                    r'braintreegateway\.com',
                    r'braintree.*checkout',
                    r'braintree.*js'
                ],
                'domains': ['braintreegateway.com'],
                'forms': [r'action.*braintree'],
                'classes': ['braintree'],
                'keywords': ['braintree']
            },
            '2Checkout': {
                'scripts': [
                    r'2checkout\.com',
                    r'2co\.com',
                    r'checkout.*2co'
                ],
                'domains': ['2checkout.com', '2co.com'],
                'forms': [r'action.*2checkout', r'action.*2co'],
                'classes': ['twocheckout', '2checkout'],
                'keywords': ['2checkout', '2co']
            },
            'Authorize.Net': {
                'scripts': [
                    r'authorize\.net',
                    r'authorizenet',
                    r'acceptjs\.js'
                ],
                'domains': ['authorize.net'],
                'forms': [r'action.*authorize'],
                'classes': ['authorize-net', 'authorizenet'],
                'keywords': ['authorize.net', 'authorizenet']
            },
            'Worldpay': {
                'scripts': [
                    r'worldpay\.com',
                    r'secure\.worldpay\.com'
                ],
                'domains': ['worldpay.com'],
                'forms': [r'action.*worldpay'],
                'classes': ['worldpay'],
                'keywords': ['worldpay']
            },
            'PayU': {
                'scripts': [
                    r'payu\.com',
                    r'payu\..*',
                    r'secure\.payu\.com'
                ],
                'domains': ['payu.com'],
                'forms': [r'action.*payu'],
                'classes': ['payu'],
                'keywords': ['payu']
            },
            'Razorpay': {
                'scripts': [
                    r'razorpay\.com',
                    r'checkout.*razorpay'
                ],
                'domains': ['razorpay.com'],
                'forms': [r'action.*razorpay'],
                'classes': ['razorpay'],
                'keywords': ['razorpay']
            },
            'Mollie': {
                'scripts': [
                    r'mollie\.com',
                    r'mollie.*checkout'
                ],
                'domains': ['mollie.com'],
                'forms': [r'action.*mollie'],
                'classes': ['mollie'],
                'keywords': ['mollie']
            },
            
            # Crypto Gateways
            'Coinbase Commerce': {
                'scripts': [
                    r'commerce\.coinbase\.com',
                    r'coinbase.*commerce'
                ],
                'domains': ['commerce.coinbase.com'],
                'forms': [r'action.*coinbase'],
                'classes': ['coinbase', 'coinbase-commerce'],
                'keywords': ['coinbase commerce']
            },
            'BitPay': {
                'scripts': [
                    r'bitpay\.com',
                    r'checkout.*bitpay'
                ],
                'domains': ['bitpay.com'],
                'forms': [r'action.*bitpay'],
                'classes': ['bitpay'],
                'keywords': ['bitpay']
            },
            'CoinPayments': {
                'scripts': [
                    r'coinpayments\.net',
                    r'checkout.*coinpayments'
                ],
                'domains': ['coinpayments.net'],
                'forms': [r'action.*coinpayments'],
                'classes': ['coinpayments'],
                'keywords': ['coinpayments']
            }
        }
    
    def detect_gateways(self, html_content: str, url: str = '') -> List[Dict[str, Any]]:
        """
        Detect payment gateways in HTML content
        
        Args:
            html_content: HTML content to analyze
            url: Source URL for context
            
        Returns:
            List of detected gateways with evidence
        """
        detected_gateways = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            html_text = html_content.lower()
            
            logger.debug(f"Analyzing payment gateways for: {url}")
            
            for gateway_name, signatures in self.gateway_signatures.items():
                evidence = []
                
                # Check script sources
                for script_pattern in signatures.get('scripts', []):
                    if self._find_script_evidence(soup, script_pattern):
                        evidence.append(f"Script: {script_pattern}")
                
                # Check form actions
                for form_pattern in signatures.get('forms', []):
                    if self._find_form_evidence(soup, form_pattern):
                        evidence.append(f"Form: {form_pattern}")
                
                # Check CSS classes
                for class_pattern in signatures.get('classes', []):
                    if self._find_class_evidence(soup, class_pattern):
                        evidence.append(f"CSS Class: {class_pattern}")
                
                # Check keywords in text
                for keyword in signatures.get('keywords', []):
                    if keyword.lower() in html_text:
                        evidence.append(f"Keyword: {keyword}")
                
                # Check domains in URL or content
                for domain in signatures.get('domains', []):
                    if domain.lower() in html_text or domain.lower() in url.lower():
                        evidence.append(f"Domain: {domain}")
                
                # If evidence found, add to detected gateways
                if evidence:
                    detected_gateways.append({
                        'name': gateway_name,
                        'evidence': evidence,
                        'confidence': self._calculate_confidence(evidence)
                    })
            
            logger.debug(f"Found {len(detected_gateways)} payment gateways")
            return detected_gateways
            
        except Exception as e:
            logger.error(f"Error detecting gateways: {e}")
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
    
    def _find_form_evidence(self, soup: BeautifulSoup, pattern: str) -> bool:
        """Find evidence in form elements"""
        try:
            forms = soup.find_all('form')
            for form in forms:
                action = form.get('action', '').lower()
                if re.search(pattern, action, re.IGNORECASE):
                    return True
                
                # Check form content
                form_text = form.get_text().lower()
                if re.search(pattern, form_text, re.IGNORECASE):
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
    
    def _calculate_confidence(self, evidence: List[str]) -> str:
        """Calculate confidence level based on evidence"""
        evidence_count = len(evidence)
        
        if evidence_count >= 3:
            return 'high'
        elif evidence_count == 2:
            return 'medium'
        else:
            return 'low'
    
    def get_gateway_summary(self, detected_gateways: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate summary of detected payment gateways
        
        Args:
            detected_gateways: List of detected gateways
            
        Returns:
            Summary dictionary
        """
        if not detected_gateways:
            return {
                'total_gateways': 0,
                'gateway_names': [],
                'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
                'categories': {'brazilian': 0, 'international': 0, 'crypto': 0}
            }
        
        gateway_names = [gw['name'] for gw in detected_gateways]
        confidence_dist = {'high': 0, 'medium': 0, 'low': 0}
        
        for gateway in detected_gateways:
            confidence = gateway.get('confidence', 'low')
            confidence_dist[confidence] = confidence_dist.get(confidence, 0) + 1
        
        # Categorize gateways
        brazilian_gateways = ['PagSeguro', 'Mercado Pago', 'Cielo', 'Rede', 'GetNet', 'Yapay', 'Pagar.me', 'Boleto Bancário']
        crypto_gateways = ['Coinbase Commerce', 'BitPay', 'CoinPayments']
        
        categories = {'brazilian': 0, 'international': 0, 'crypto': 0}
        
        for name in gateway_names:
            if name in brazilian_gateways:
                categories['brazilian'] += 1
            elif name in crypto_gateways:
                categories['crypto'] += 1
            else:
                categories['international'] += 1
        
        return {
            'total_gateways': len(detected_gateways),
            'gateway_names': gateway_names,
            'confidence_distribution': confidence_dist,
            'categories': categories
        }