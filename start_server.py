#!/usr/bin/env python3
"""
Script para iniciar o servidor de email com credenciais pré-configuradas
"""
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def main():
    print("🚀 Iniciando Email Client - T-Online")
    print("=" * 50)
    print("📧 Email: chrissi-x@t-online.de")
    print("🔗 Servidor: secureimap.t-online.de:993")
    print("🌐 Interface: http://localhost:5000")
    print("=" * 50)
    
    # Verificar se o ambiente virtual está ativo
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Ambiente virtual não detectado!")
        print("Execute: source venv/bin/activate")
        return
    
    # Verificar se as dependências estão instaladas
    try:
        import flask
        import flask_socketio
        print("✅ Dependências verificadas")
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("Execute: pip install -r requirements.txt")
        return
    
    # Iniciar o servidor
    print("\n🎯 Iniciando servidor...")
    print("📱 Acesse: http://localhost:5000")
    print("🔑 Use as credenciais:")
    print("   Email: chrissi-x@t-online.de")
    print("   Senha: Chrissdcaja23")
    print("\n⏹️  Para parar o servidor, pressione Ctrl+C")
    print("=" * 50)
    
    # Importar e executar o app
    from app import app, socketio
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main()