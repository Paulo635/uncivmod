# Email Client - Cliente de Email IMAP

Um cliente de email web moderno que se conecta a servidores IMAP para visualizar emails em tempo real.

## 🚀 Funcionalidades

- **Conexão IMAP**: Suporte a múltiplos provedores de email (Gmail, Outlook, Yahoo, etc.)
- **Interface Moderna**: Design responsivo e intuitivo
- **Tempo Real**: Atualizações automáticas via WebSocket
- **Busca**: Pesquisa em emails por assunto, remetente ou conteúdo
- **Múltiplas Pastas**: Navegação entre diferentes pastas de email
- **Visualização Detalhada**: Visualização completa de emails
- **Estatísticas**: Contadores de emails e status de conexão

## 📋 Pré-requisitos

- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)
- Conta de email com acesso IMAP habilitado

## 🛠️ Instalação

1. **Clone ou baixe o projeto**
   ```bash
   git clone <url-do-repositorio>
   cd email-client
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

4. **Execute o servidor**
   ```bash
   python app.py
   ```

5. **Acesse a aplicação**
   - Abra seu navegador
   - Vá para `http://localhost:5000`

## 🔧 Configuração

### Configuração do Gmail

Para usar com Gmail, você precisa:

1. **Habilitar autenticação de 2 fatores** na sua conta Google
2. **Gerar uma senha de app**:
   - Vá para [Configurações da Conta Google](https://myaccount.google.com/)
   - Segurança → Verificação em duas etapas → Senhas de app
   - Gere uma senha para "Email"
3. **Use essa senha** no login da aplicação

### Outros Provedores

| Provedor | Servidor IMAP | Porta |
|----------|---------------|-------|
| Gmail | imap.gmail.com | 993 |
| Outlook | outlook.office365.com | 993 |
| Yahoo | imap.mail.yahoo.com | 993 |
| iCloud | imap.mail.me.com | 993 |

## 📱 Como Usar

### 1. Login
- Digite seu endereço de email
- Digite sua senha (ou senha de app para Gmail)
- Clique em "Conectar"

### 2. Navegação
- **Caixa de Entrada**: Visualize emails recebidos
- **Pastas**: Navegue entre diferentes pastas
- **Busca**: Use a barra de pesquisa para encontrar emails
- **Atualizar**: Clique no botão para atualizar manualmente

### 3. Visualização de Emails
- Clique em qualquer email para ver o conteúdo completo
- Use o botão X para fechar a visualização detalhada

### 4. Controles
- **Limite de emails**: Escolha quantos emails carregar
- **Status de conexão**: Veja se está conectado ao servidor
- **Logout**: Clique em "Sair" para desconectar

## 🔒 Segurança

⚠️ **Importante**: Esta aplicação é para uso educacional e de desenvolvimento. Para uso em produção:

1. **Use HTTPS**: Configure SSL/TLS
2. **Altere a SECRET_KEY**: Use uma chave secreta forte
3. **Implemente autenticação**: Adicione sistema de usuários
4. **Configure CORS**: Restrinja origens permitidas
5. **Use variáveis de ambiente**: Não commite credenciais

## 🐛 Solução de Problemas

### Erro de Conexão
- Verifique se o servidor IMAP está correto
- Confirme se a porta está correta (geralmente 993 para SSL)
- Para Gmail, use senha de app, não sua senha normal

### Emails não aparecem
- Verifique se a pasta está correta
- Tente aumentar o limite de emails
- Use o botão "Atualizar"

### Interface não carrega
- Verifique se o servidor está rodando
- Confirme se acessou `http://localhost:5000`
- Verifique o console do navegador para erros

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
email-client/
├── app.py              # Servidor Flask principal
├── requirements.txt    # Dependências Python
├── .env               # Configurações de ambiente
├── templates/
│   └── index.html     # Template HTML principal
├── static/
│   ├── css/
│   │   └── style.css  # Estilos CSS
│   └── js/
│       └── app.js     # JavaScript do frontend
└── README.md          # Este arquivo
```

### Tecnologias Utilizadas
- **Backend**: Flask, Flask-SocketIO, imaplib
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Comunicação**: WebSocket (Socket.IO)
- **Estilização**: CSS customizado com design responsivo

### Adicionando Novas Funcionalidades
1. **Backend**: Adicione rotas em `app.py`
2. **Frontend**: Modifique `static/js/app.js`
3. **Interface**: Atualize `templates/index.html` e `static/css/style.css`

## 📄 Licença

Este projeto é de código aberto e está disponível sob a licença MIT.

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Se você encontrar problemas ou tiver dúvidas:

1. Verifique a seção de solução de problemas
2. Consulte a documentação do IMAP
3. Abra uma issue no repositório

---

**Nota**: Este é um projeto educacional. Use com responsabilidade e sempre respeite as políticas de uso dos provedores de email.