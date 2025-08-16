#!/usr/bin/env python3
import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv()

def test_imap_connection():
    # Configurações
    IMAP_SERVER = os.getenv('IMAP_SERVER', 'secureimap.t-online.de')
    IMAP_PORT = int(os.getenv('IMAP_PORT', 993))
    EMAIL = 'chrissi-x@t-online.de'
    PASSWORD = 'Chrissdcaja23'
    
    print(f"Testando conexão com {IMAP_SERVER}:{IMAP_PORT}")
    print(f"Email: {EMAIL}")
    
    try:
        # Conectar ao servidor IMAP
        print("Conectando ao servidor IMAP...")
        connection = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        
        # Fazer login
        print("Fazendo login...")
        connection.login(EMAIL, PASSWORD)
        print("✅ Login realizado com sucesso!")
        
        # Listar pastas
        print("\n📁 Pastas disponíveis:")
        _, folders = connection.list()
        for folder in folders:
            folder_name = folder.decode().split('"')[-2]
            if folder_name:
                print(f"  - {folder_name}")
        
        # Selecionar caixa de entrada
        print("\n📬 Acessando caixa de entrada...")
        connection.select('INBOX')
        
        # Buscar emails
        print("Buscando emails...")
        _, message_numbers = connection.search(None, 'ALL')
        
        if message_numbers[0]:
            email_list = message_numbers[0].split()
            total_emails = len(email_list)
            print(f"✅ Encontrados {total_emails} emails na caixa de entrada")
            
            # Mostrar os últimos 5 emails
            print("\n📧 Últimos 5 emails:")
            for i, num in enumerate(email_list[-5:]):
                _, msg_data = connection.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject = decode_header(email_message["subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_addr = decode_header(email_message["from"])[0][0]
                if isinstance(from_addr, bytes):
                    from_addr = from_addr.decode()
                
                date = email_message["date"]
                
                print(f"  {i+1}. Assunto: {subject or 'Sem assunto'}")
                print(f"     De: {from_addr or 'Desconhecido'}")
                print(f"     Data: {date or 'Data desconhecida'}")
                print()
        else:
            print("📭 Caixa de entrada vazia")
        
        # Fechar conexão
        connection.logout()
        print("✅ Conexão fechada com sucesso!")
        
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"❌ Erro IMAP: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testando conexão IMAP com T-Online")
    print("=" * 50)
    
    success = test_imap_connection()
    
    if success:
        print("\n🎉 Teste concluído com sucesso!")
        print("O servidor está pronto para ser executado.")
    else:
        print("\n💥 Teste falhou!")
        print("Verifique as credenciais e configurações.")