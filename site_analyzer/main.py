#!/usr/bin/env python3
"""
Site Analyzer for Payment Gateways and Security Mechanisms

A comprehensive tool to analyze websites for payment gateway integrations
and security mechanisms like CAPTCHAs, WAFs, and bot detection.

Usage:
    python main.py

Author: Site Analyzer
Version: 1.0.0
"""

import sys
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.site_parser import SiteAnalyzer
from utils.logger import logger


def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          SITE ANALYZER v1.0.0                              ║
║          Payment Gateway & Security Mechanism Detection Tool                ║
╚══════════════════════════════════════════════════════════════════════════════╝

🎯 Analisador de Sites para Gateways e Segurança
   • Detecta gateways brasileiros e internacionais  
   • Identifica CAPTCHAs, WAFs e proteções anti-bot
   • Análise paralela e robusta com precisão cirúrgica
   • Relatórios detalhados em JSON/CSV
"""
    print(banner)


def get_user_input():
    """Get search term and configuration from user"""
    print("📝 CONFIGURAÇÃO DA ANÁLISE")
    print("-" * 50)
    
    # Get search term
    while True:
        search_term = input("Digite o termo de pesquisa: ").strip()
        if search_term:
            break
        print("❌ Termo de pesquisa não pode estar vazio!")
    
    # Get number of URLs
    while True:
        try:
            max_urls_input = input("Número máximo de URLs para analisar [20]: ").strip()
            max_urls = int(max_urls_input) if max_urls_input else 20
            if 1 <= max_urls <= 100:
                break
            else:
                print("❌ Número deve estar entre 1 e 100!")
        except ValueError:
            print("❌ Digite um número válido!")
    
    # Get output format
    while True:
        output_format = input("Formato de saída (json/csv) [json]: ").strip().lower()
        if not output_format:
            output_format = 'json'
        if output_format in ['json', 'csv']:
            break
        print("❌ Formato deve ser 'json' ou 'csv'!")
    
    return search_term, max_urls, output_format


def main():
    """Main execution function"""
    print_banner()
    
    try:
        # Get user input
        search_term, max_urls, output_format = get_user_input()
        
        print(f"\n🚀 INICIANDO ANÁLISE")
        print("-" * 50)
        print(f"   • Termo: '{search_term}'")
        print(f"   • URLs: {max_urls}")
        print(f"   • Formato: {output_format.upper()}")
        print()
        
        # Initialize analyzer
        analyzer = SiteAnalyzer(max_workers=10)
        
        # Perform analysis
        results = analyzer.analyze_search_term(search_term, max_urls)
        
        # Print results summary
        analyzer.print_summary(results)
        
        # Save results to file
        output_file = analyzer.save_results(results, output_format)
        
        print(f"\n💾 ARQUIVO SALVO: {output_file}")
        
        # Show detailed results for top domains
        print_detailed_results(results)
        
        logger.success("Análise concluída com sucesso!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Análise interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro durante a análise: {e}")
        sys.exit(1)


def print_detailed_results(results):
    """Print detailed results for inspection"""
    print("\n🔍 DETALHES DOS RESULTADOS")
    print("=" * 80)
    
    successful_results = [r for r in results.get('results', []) if r['status'] == 'success']
    
    # Show top 10 results with details
    for i, result in enumerate(successful_results[:10], 1):
        print(f"\n{i}. {result['domain']}")
        print(f"   URL: {result['url']}")
        
        # Payment gateways
        gateways = result.get('gateways', [])
        if gateways:
            print(f"   💳 Gateways ({len(gateways)}):")
            for gw in gateways:
                confidence = gw.get('confidence', 'low')
                evidence_count = len(gw.get('evidence', []))
                print(f"      • {gw['name']} (confiança: {confidence}, evidências: {evidence_count})")
        else:
            print(f"   💳 Nenhum gateway detectado")
        
        # Security mechanisms
        security = result.get('security_mechanisms', [])
        if security:
            print(f"   🔒 Segurança ({len(security)}):")
            for sec in security:
                confidence = sec.get('confidence', 'low')
                category = sec.get('category', 'other')
                print(f"      • {sec['name']} ({category}, confiança: {confidence})")
        else:
            print(f"   🔒 Nenhum mecanismo de segurança detectado")
        
        # Security headers
        security_headers = result.get('security_headers', {})
        security_score = security_headers.get('security_score', 0)
        print(f"   📊 Score de segurança: {security_score:.1f}%")
        
        if i >= 10:
            remaining = len(successful_results) - 10
            if remaining > 0:
                print(f"\n... e mais {remaining} sites analisados (veja o arquivo de saída)")
            break


def cli_mode():
    """Command line interface mode"""
    parser = argparse.ArgumentParser(
        description="Site Analyzer - Detecta gateways de pagamento e mecanismos de segurança",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'search_term',
        help='Termo de pesquisa para análise'
    )
    
    parser.add_argument(
        '-n', '--max-urls',
        type=int,
        default=20,
        help='Número máximo de URLs para analisar (default: 20)'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['json', 'csv'],
        default='json',
        help='Formato de saída (default: json)'
    )
    
    parser.add_argument(
        '-w', '--workers',
        type=int,
        default=10,
        help='Número de workers paralelos (default: 10)'
    )
    
    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Não mostrar resumo no console'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.search_term.strip():
        print("❌ Erro: Termo de pesquisa não pode estar vazio!")
        sys.exit(1)
    
    if not (1 <= args.max_urls <= 100):
        print("❌ Erro: Número de URLs deve estar entre 1 e 100!")
        sys.exit(1)
    
    if not (1 <= args.workers <= 50):
        print("❌ Erro: Número de workers deve estar entre 1 e 50!")
        sys.exit(1)
    
    print_banner()
    
    try:
        print(f"🚀 ANÁLISE EM MODO CLI")
        print("-" * 50)
        print(f"   • Termo: '{args.search_term}'")
        print(f"   • URLs: {args.max_urls}")
        print(f"   • Formato: {args.format.upper()}")
        print(f"   • Workers: {args.workers}")
        print()
        
        # Initialize analyzer
        analyzer = SiteAnalyzer(max_workers=args.workers)
        
        # Perform analysis
        results = analyzer.analyze_search_term(args.search_term, args.max_urls)
        
        # Print results summary
        if not args.no_summary:
            analyzer.print_summary(results)
        
        # Save results to file
        output_file = analyzer.save_results(results, args.format)
        
        print(f"\n💾 ARQUIVO SALVO: {output_file}")
        
        logger.success("Análise concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a análise: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if running in CLI mode (command line arguments provided)
    if len(sys.argv) > 1:
        cli_mode()
    else:
        main()