#!/usr/bin/env python3
"""
Demo script for Site Analyzer
Demonstrates the tool's capabilities with a predefined search term
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.site_parser import SiteAnalyzer
from utils.logger import logger


def run_demo():
    """Run a demonstration of the site analyzer"""
    
    print("🎯 SITE ANALYZER - DEMONSTRAÇÃO")
    print("="*50)
    print("Executando análise demo com termo: 'loja de roupas online'")
    print("Analisando 10 URLs para demonstração...")
    print()
    
    try:
        # Initialize analyzer
        analyzer = SiteAnalyzer(max_workers=5)  # Reduced workers for demo
        
        # Run analysis with demo term
        search_term = "loja de roupas online"
        results = analyzer.analyze_search_term(search_term, max_urls=10)
        
        # Print summary
        analyzer.print_summary(results)
        
        # Save demo results
        json_file = analyzer.save_results(results, 'json')
        csv_file = analyzer.save_results(results, 'csv')
        
        print(f"\n📁 ARQUIVOS GERADOS:")
        print(f"   • JSON: {json_file}")
        print(f"   • CSV: {csv_file}")
        
        # Show some detailed results
        print("\n🔍 EXEMPLOS DETALHADOS:")
        print("-"*50)
        
        successful_results = [r for r in results.get('results', []) if r['status'] == 'success']
        
        for i, result in enumerate(successful_results[:3], 1):
            print(f"\n{i}. {result['domain']}")
            
            gateways = result.get('gateways', [])
            if gateways:
                gateway_names = [gw['name'] for gw in gateways]
                print(f"   💳 Gateways: {', '.join(gateway_names)}")
            
            security = result.get('security_mechanisms', [])
            if security:
                security_names = [sec['name'] for sec in security]
                print(f"   🔒 Segurança: {', '.join(security_names)}")
            
            security_score = result.get('security_headers', {}).get('security_score', 0)
            print(f"   📊 Score segurança: {security_score:.1f}%")
        
        print("\n✅ DEMONSTRAÇÃO CONCLUÍDA!")
        print("Execute 'python main.py' para usar interativamente")
        
    except Exception as e:
        logger.error(f"Erro na demonstração: {e}")
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    run_demo()