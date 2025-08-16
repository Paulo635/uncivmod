#!/usr/bin/env python3
"""
Servidor público para o Email Client
"""
import socket
import threading
import http.server
import socketserver
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def get_public_ip():
    """Obtém o IP público do servidor"""
    try:
        import requests
        response = requests.get('https://api.ipify.org', timeout=5)
        return response.text
    except:
        return "IP público não disponível"

def get_local_ip():
    """Obtém o IP local do servidor"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def start_flask_server():
    """Inicia o servidor Flask em background"""
    os.system("source venv/bin/activate && python app.py &")

def main():
    print("🌐 Iniciando Email Client - Servidor Público")
    print("=" * 60)
    
    # Obter IPs
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"🏠 IP Local: {local_ip}")
    print(f"🌍 IP Público: {public_ip}")
    print(f"🔗 URLs de acesso:")
    print(f"   Local: http://{local_ip}:5000")
    print(f"   Público: http://{public_ip}:5000")
    print("=" * 60)
    
    # Iniciar servidor Flask
    print("🚀 Iniciando servidor Flask...")
    start_flask_server()
    
    # Aguardar um pouco
    import time
    time.sleep(3)
    
    print("✅ Servidor iniciado!")
    print("📧 Email: chrissi-x@t-online.de")
    print("🔑 Senha: Chrissdcaja23")
    print("=" * 60)
    print("🌐 Acesse uma das URLs acima")
    print("⏹️  Para parar: Ctrl+C")
    
    # Manter o script rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        os.system("pkill -f 'python app.py'")
        print("✅ Servidor parado!")

if __name__ == "__main__":
    main()