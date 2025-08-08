import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import json
import csv
from datetime import datetime
from pathlib import Path
import sys

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.serpapi_client import SerpApiClient
from core.gateway_detector import GatewayDetector
from core.security_detector import SecurityDetector
from utils.http_utils import HTTPClient
from utils.logger import logger


class SiteAnalyzer:
    """Main site analyzer that orchestrates all analysis components"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.serpapi_client = SerpApiClient()
        self.gateway_detector = GatewayDetector()
        self.security_detector = SecurityDetector()
        self.http_client = HTTPClient()
        
    def analyze_search_term(self, search_term: str, max_urls: int = 20) -> Dict[str, Any]:
        """
        Analyze all sites from a search term
        
        Args:
            search_term: Search query for SerpApi
            max_urls: Maximum number of URLs to analyze
            
        Returns:
            Complete analysis results
        """
        logger.info(f"Starting analysis for search term: '{search_term}'")
        
        # Step 1: Get URLs from SerpApi
        search_results = self.serpapi_client.search(search_term, max_urls)
        
        if not search_results:
            logger.warning("No search results found")
            return {
                'search_term': search_term,
                'total_urls': 0,
                'analyzed_urls': 0,
                'results': [],
                'summary': {},
                'timestamp': datetime.now().isoformat()
            }
        
        search_summary = self.serpapi_client.get_search_results_summary(search_results)
        logger.info(f"Found {search_summary['total_results']} URLs from {search_summary['unique_domains']} domains")
        
        # Step 2: Analyze each URL
        urls_to_analyze = [result['url'] for result in search_results]
        logger.info(f"Analyzing {len(urls_to_analyze)} URLs...")
        
        analysis_results = self._analyze_urls_parallel(urls_to_analyze)
        
        # Step 3: Generate comprehensive summary
        summary = self._generate_summary(analysis_results)
        
        # Step 4: Compile final results
        final_results = {
            'search_term': search_term,
            'total_urls': len(search_results),
            'analyzed_urls': len([r for r in analysis_results if r['status'] == 'success']),
            'results': analysis_results,
            'summary': summary,
            'search_summary': search_summary,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.success(f"Analysis complete! Successfully analyzed {final_results['analyzed_urls']}/{final_results['total_urls']} URLs")
        
        return final_results
    
    def _analyze_urls_parallel(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze URLs in parallel using ThreadPoolExecutor
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_url = {executor.submit(self._analyze_single_url, url): url for url in urls}
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Log progress
                    if result['status'] == 'success':
                        gateways = [gw['name'] for gw in result.get('gateways', [])]
                        security = [sec['name'] for sec in result.get('security_mechanisms', [])]
                        logger.info(f"✅ {result['domain']} - Gateways: {gateways} - Security: {security}")
                    else:
                        logger.warning(f"❌ {result['domain']} - {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    logger.error(f"Exception analyzing {url}: {e}")
                    results.append({
                        'url': url,
                        'domain': self._extract_domain(url),
                        'status': 'error',
                        'error': str(e),
                        'gateways': [],
                        'security_mechanisms': []
                    })
        
        return results
    
    def _analyze_single_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a single URL for payment gateways and security mechanisms
        
        Args:
            url: URL to analyze
            
        Returns:
            Analysis result dictionary
        """
        domain = self._extract_domain(url)
        
        try:
            # Fetch URL with security info
            http_result = self.http_client.get_with_security_info(url)
            
            if http_result['status'] != 'success' or not http_result['response']:
                return {
                    'url': url,
                    'domain': domain,
                    'status': 'failed',
                    'error': 'Could not fetch URL',
                    'gateways': [],
                    'security_mechanisms': [],
                    'security_headers': {}
                }
            
            response = http_result['response']
            headers = http_result['headers']
            
            # Detect payment gateways
            gateways = self.gateway_detector.detect_gateways(response.text, url)
            
            # Detect security mechanisms
            security_mechanisms = self.security_detector.detect_security_mechanisms(
                response.text, headers, url
            )
            
            # Analyze security headers
            security_headers = self.security_detector.check_security_headers(headers)
            
            return {
                'url': url,
                'domain': domain,
                'status': 'success',
                'gateways': gateways,
                'security_mechanisms': security_mechanisms,
                'security_headers': security_headers,
                'server_info': http_result.get('server_info', {}),
                'response_size': len(response.text),
                'status_code': response.status_code
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {url}: {e}")
            return {
                'url': url,
                'domain': domain,
                'status': 'error',
                'error': str(e),
                'gateways': [],
                'security_mechanisms': [],
                'security_headers': {}
            }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return url
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive summary of analysis results
        
        Args:
            results: List of analysis results
            
        Returns:
            Summary dictionary
        """
        successful_results = [r for r in results if r['status'] == 'success']
        failed_results = [r for r in results if r['status'] != 'success']
        
        # Gateway analysis
        all_gateways = []
        for result in successful_results:
            all_gateways.extend(result.get('gateways', []))
        
        gateway_summary = self.gateway_detector.get_gateway_summary(all_gateways)
        
        # Security analysis
        all_security = []
        for result in successful_results:
            all_security.extend(result.get('security_mechanisms', []))
        
        security_summary = self.security_detector.get_security_summary(all_security)
        
        # Top domains with gateways/security
        domain_stats = {}
        for result in successful_results:
            domain = result['domain']
            if domain not in domain_stats:
                domain_stats[domain] = {
                    'gateways': [],
                    'security': [],
                    'gateway_count': 0,
                    'security_count': 0
                }
            
            gateway_names = [gw['name'] for gw in result.get('gateways', [])]
            security_names = [sec['name'] for sec in result.get('security_mechanisms', [])]
            
            domain_stats[domain]['gateways'] = gateway_names
            domain_stats[domain]['security'] = security_names
            domain_stats[domain]['gateway_count'] = len(gateway_names)
            domain_stats[domain]['security_count'] = len(security_names)
        
        # Sort domains by total protections
        top_domains = sorted(
            domain_stats.items(),
            key=lambda x: x[1]['gateway_count'] + x[1]['security_count'],
            reverse=True
        )[:10]
        
        return {
            'total_analyzed': len(successful_results),
            'total_failed': len(failed_results),
            'success_rate': len(successful_results) / len(results) * 100 if results else 0,
            'gateway_summary': gateway_summary,
            'security_summary': security_summary,
            'top_domains': dict(top_domains),
            'failure_reasons': [r.get('error', 'Unknown') for r in failed_results]
        }
    
    def save_results(self, results: Dict[str, Any], output_format: str = 'json') -> str:
        """
        Save analysis results to file
        
        Args:
            results: Analysis results to save
            output_format: Output format ('json' or 'csv')
            
        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        search_term = results.get('search_term', 'unknown').replace(' ', '_')
        
        if output_format.lower() == 'json':
            filename = f"site_analysis_{search_term}_{timestamp}.json"
            filepath = Path(filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.success(f"Results saved to {filepath}")
            return str(filepath)
        
        elif output_format.lower() == 'csv':
            filename = f"site_analysis_{search_term}_{timestamp}.csv"
            filepath = Path(filename)
            
            # Flatten results for CSV
            csv_data = []
            for result in results.get('results', []):
                row = {
                    'url': result.get('url', ''),
                    'domain': result.get('domain', ''),
                    'status': result.get('status', ''),
                    'gateways': ', '.join([gw['name'] for gw in result.get('gateways', [])]),
                    'security_mechanisms': ', '.join([sec['name'] for sec in result.get('security_mechanisms', [])]),
                    'gateway_count': len(result.get('gateways', [])),
                    'security_count': len(result.get('security_mechanisms', [])),
                    'security_score': result.get('security_headers', {}).get('security_score', 0)
                }
                csv_data.append(row)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if csv_data:
                    writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                    writer.writeheader()
                    writer.writerows(csv_data)
            
            logger.success(f"Results saved to {filepath}")
            return str(filepath)
        
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    def print_summary(self, results: Dict[str, Any]):
        """
        Print a formatted summary to console
        
        Args:
            results: Analysis results
        """
        print("\n" + "="*80)
        print(f"SITE ANALYSIS RESULTS - {results.get('search_term', 'Unknown Query')}")
        print("="*80)
        
        summary = results.get('summary', {})
        
        print(f"\n📊 OVERVIEW:")
        print(f"   • Total URLs analyzed: {results.get('analyzed_urls', 0)}/{results.get('total_urls', 0)}")
        print(f"   • Success rate: {summary.get('success_rate', 0):.1f}%")
        
        # Gateway summary
        gateway_summary = summary.get('gateway_summary', {})
        if gateway_summary.get('total_gateways', 0) > 0:
            print(f"\n💳 PAYMENT GATEWAYS:")
            print(f"   • Total detected: {gateway_summary['total_gateways']}")
            print(f"   • Brazilian: {gateway_summary['categories']['brazilian']}")
            print(f"   • International: {gateway_summary['categories']['international']}")
            print(f"   • Crypto: {gateway_summary['categories']['crypto']}")
            print(f"   • Top gateways: {', '.join(gateway_summary['gateway_names'][:5])}")
        
        # Security summary
        security_summary = summary.get('security_summary', {})
        if security_summary.get('total_mechanisms', 0) > 0:
            print(f"\n🔒 SECURITY MECHANISMS:")
            print(f"   • Total detected: {security_summary['total_mechanisms']}")
            print(f"   • CAPTCHAs: {security_summary['categories']['captcha']}")
            print(f"   • WAFs: {security_summary['categories']['waf']}")
            print(f"   • Bot Detection: {security_summary['categories']['bot_detection']}")
            print(f"   • Top mechanisms: {', '.join(security_summary['mechanism_names'][:5])}")
        
        # Top domains
        top_domains = summary.get('top_domains', {})
        if top_domains:
            print(f"\n🏆 TOP PROTECTED DOMAINS:")
            for i, (domain, stats) in enumerate(list(top_domains.items())[:5], 1):
                gateways = ', '.join(stats['gateways'][:3]) if stats['gateways'] else 'None'
                security = ', '.join(stats['security'][:3]) if stats['security'] else 'None'
                print(f"   {i}. {domain}")
                print(f"      Gateways: {gateways}")
                print(f"      Security: {security}")
        
        print("\n" + "="*80)
    
    def __del__(self):
        """Cleanup resources"""
        try:
            self.http_client.close()
        except Exception:
            pass