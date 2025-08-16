import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime
import json
import threading
import time
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import base64

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*")

# Configurações IMAP
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')
IMAP_PORT = int(os.getenv('IMAP_PORT', 993))

class EmailClient:
    def __init__(self):
        self.connection = None
        self.is_connected = False
        
    def connect(self, email_address, password):
        try:
            self.connection = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
            self.connection.login(email_address, password)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Erro de conexão: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.logout()
            self.is_connected = False
    
    def get_emails(self, folder='INBOX', limit=50):
        if not self.is_connected:
            return []
        
        try:
            self.connection.select(folder)
            _, message_numbers = self.connection.search(None, 'ALL')
            
            emails = []
            message_list = message_numbers[0].split()
            
            # Pegar os últimos emails
            for num in message_list[-limit:]:
                _, msg_data = self.connection.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                subject = decode_header(email_message["subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                
                from_addr = decode_header(email_message["from"])[0][0]
                if isinstance(from_addr, bytes):
                    from_addr = from_addr.decode()
                
                date = email_message["date"]
                
                # Extrair texto do email
                body = ""
                if email_message.is_multipart():
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = email_message.get_payload(decode=True).decode()
                
                emails.append({
                    'id': num.decode(),
                    'subject': subject or 'Sem assunto',
                    'from': from_addr or 'Desconhecido',
                    'date': date or 'Data desconhecida',
                    'body': body[:200] + '...' if len(body) > 200 else body,
                    'full_body': body
                })
            
            return emails[::-1]  # Inverter para mostrar mais recentes primeiro
            
        except Exception as e:
            print(f"Erro ao buscar emails: {e}")
            return []
    
    def get_folders(self):
        if not self.is_connected:
            return []
        
        try:
            _, folders = self.connection.list()
            folder_list = []
            for folder in folders:
                folder_name = folder.decode().split('"')[-2]
                if folder_name:
                    folder_list.append(folder_name)
            return folder_list
        except Exception as e:
            print(f"Erro ao buscar pastas: {e}")
            return []

email_client = EmailClient()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email_address = data.get('email')
    password = data.get('password')
    
    if email_client.connect(email_address, password):
        session['email'] = email_address
        return jsonify({'success': True, 'message': 'Login realizado com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Falha no login. Verifique suas credenciais.'})

@app.route('/logout')
def logout():
    email_client.disconnect()
    session.pop('email', None)
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso!'})

@app.route('/emails')
def get_emails():
    if not email_client.is_connected:
        return jsonify({'success': False, 'message': 'Não conectado'})
    
    folder = request.args.get('folder', 'INBOX')
    limit = int(request.args.get('limit', 50))
    
    emails = email_client.get_emails(folder, limit)
    return jsonify({'success': True, 'emails': emails})

@app.route('/folders')
def get_folders():
    if not email_client.is_connected:
        return jsonify({'success': False, 'message': 'Não conectado'})
    
    folders = email_client.get_folders()
    return jsonify({'success': True, 'folders': folders})

def background_email_checker():
    """Verifica novos emails em background e envia via WebSocket"""
    while True:
        if email_client.is_connected:
            try:
                emails = email_client.get_emails('INBOX', 5)  # Últimos 5 emails
                socketio.emit('new_emails', {'emails': emails})
            except Exception as e:
                print(f"Erro no background checker: {e}")
        time.sleep(30)  # Verificar a cada 30 segundos

# Iniciar thread de verificação em background
email_checker_thread = threading.Thread(target=background_email_checker, daemon=True)
email_checker_thread.start()

@socketio.on('connect')
def handle_connect():
    print('Cliente conectado via WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado via WebSocket')

if __name__ == '__main__':
    print("🚀 Iniciando Email Client...")
    print("📧 Email: chrissi-x@t-online.de")
    print("🔗 Servidor IMAP: secureimap.t-online.de")
    print("🌐 Interface: http://0.0.0.0:5000")
    print("=" * 50)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)