#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ferramenta de Identificação de Gateway de Pagamento e Geração de Dorks
Uso ético e técnico. Detecta gateways em uma URL e gera dorks para busca.
"""
import sys
import os
import argparse
import csv
from urllib.parse import urlparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'core'))
sys.path.insert(0, str(Path(__file__).parent / 'utils'))

from core.gateway_detector import GatewayDetector
from utils.http_utils import HTTPClient

AVISO_ETICO = (
    '\033[93mAVISO: Use esta ferramenta apenas para fins legítimos, técnicos e com permissão.\033[0m\n'
    'Não utilize para exploração, invasão ou coleta não autorizada. Respeite a ética e a lei.'
)

# Dorks por gateway (padrões principais)
DORK_PATTERNS = {
    'Stripe': [
        (r'checkout.stripe.com', 'Busca URLs de checkout Stripe'),
        (r'js.stripe.com', 'Busca scripts Stripe'),
        (r'"powered by stripe"', 'Busca menções explícitas'),
    ],
    'Pagar.me': [
        (r'pagar.me', 'Busca URLs ou scripts do Pagar.me'),
        (r'"powered by pagar.me"', 'Busca menções explícitas'),
    ],
    'PagSeguro': [
        (r'pagseguro.uol.com.br', 'Busca URLs de PagSeguro'),
        (r'assets.pagseguro.com.br', 'Busca assets PagSeguro'),
        (r'"powered by pagseguro"', 'Busca menções explícitas'),
    ],
    'Mercado Pago': [
        (r'mercadopago.com', 'Busca URLs Mercado Pago'),
        (r'sdk.mercadopago.com', 'Busca scripts Mercado Pago'),
        (r'"powered by mercadopago"', 'Busca menções explícitas'),
    ],
    'PayPal': [
        (r'paypal.com', 'Busca URLs PayPal'),
        (r'paypalobjects.com', 'Busca assets PayPal'),
        (r'"powered by paypal"', 'Busca menções explícitas'),
    ],
    'Boleto Bancário': [
        (r'boleto', 'Busca menções a boleto bancário'),
    ],
    # Adicione outros gateways conforme necessário
}

# Função para gerar dorks para um gateway
def gerar_dorks(gateway_nome, url_origem, tld_filter=None):
    dorks = []
    dominio = urlparse(url_origem).netloc
    tld = tld_filter if tld_filter else '*'
    patterns = DORK_PATTERNS.get(gateway_nome, [])
    for pattern, explicacao in patterns:
        dork = f'inurl:"{pattern}" site:{tld}.com -inurl:{dominio}'
        if tld_filter:
            dork = dork.replace('.com', f'.{tld_filter}')
        dorks.append({'dork': dork, 'explicacao': explicacao})
    return dorks

# Função principal
def main():
    print(AVISO_ETICO)
    parser = argparse.ArgumentParser(
        description='Ferramenta de identificação de gateway de pagamento e geração de dorks (uso ético).'
    )
    parser.add_argument('-u', '--url', required=True, help='URL do site a ser analisado (ex: https://exemplo.com)')
    parser.add_argument('--output', help='Arquivo de saída (.txt ou .csv)')
    parser.add_argument('--tld', help='Filtrar dorks por TLD (ex: com, br)')
    parser.add_argument('--categoria', help='Filtrar por categoria (placeholder, não implementado)')
    args = parser.parse_args()

    url = args.url
    tld_filter = args.tld
    output_file = args.output

    # Validação básica da URL
    if not url.startswith('http'):
        print('URL inválida. Use o formato completo, ex: https://exemplo.com')
        sys.exit(1)

    # Respeito a robots.txt e delays já implementados no HTTPClient
    http = HTTPClient(timeout=10, max_retries=2)
    try:
        resp = http.get(url)
        if not resp or resp.status_code != 200:
            print(f'Erro ao acessar a URL: {url} (status: {getattr(resp, "status_code", "N/A")})')
            sys.exit(2)
        html = resp.text
    except Exception as e:
        print(f'Erro ao acessar a URL: {e}')
        sys.exit(2)

    detector = GatewayDetector()
    gateways = detector.detect_gateways(html, url)
    if not gateways:
        print('Nenhum gateway de pagamento detectado.')
        sys.exit(0)

    print(f'Gateways detectados:')
    all_dorks = []
    for gw in gateways:
        nome = gw["name"]
        evidencias = ", ".join(gw["evidence"])
        print(f'- {nome} (identificado por: {evidencias})')
        dorks = gerar_dorks(nome, url, tld_filter)
        if dorks:
            print('  Dorks geradas:')
            for i, d in enumerate(dorks, 1):
                print(f'   {i}. {d["dork"]} - {d["explicacao"]}')
            all_dorks.extend([{**d, 'gateway': nome} for d in dorks])
        else:
            print('  Nenhuma dork padrão para este gateway.')

    # Salvar se solicitado
    if output_file:
        ext = os.path.splitext(output_file)[1].lower()
        try:
            if ext == '.csv':
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=['gateway', 'dork', 'explicacao'])
                    writer.writeheader()
                    for d in all_dorks:
                        writer.writerow(d)
            else:
                with open(output_file, 'w', encoding='utf-8') as f:
                    for d in all_dorks:
                        f.write(f'{d["gateway"]}: {d["dork"]} # {d["explicacao"]}\n')
            print(f'Salvo em: {output_file}')
        except Exception as e:
            print(f'Erro ao salvar arquivo: {e}')

if __name__ == '__main__':
    main()