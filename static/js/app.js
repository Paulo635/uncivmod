// Configuração do Socket.IO
const socket = io();

// Elementos DOM
const loginScreen = document.getElementById('loginScreen');
const emailInterface = document.getElementById('emailInterface');
const loginForm = document.getElementById('loginForm');
const emailList = document.getElementById('emailList');
const emailDetail = document.getElementById('emailDetail');
const loadingOverlay = document.getElementById('loadingOverlay');
const notification = document.getElementById('notification');
const notificationMessage = document.getElementById('notificationMessage');
const connectionStatus = document.getElementById('connectionStatus');
const currentFolder = document.getElementById('currentFolder');
const totalEmails = document.getElementById('totalEmails');
const unreadEmails = document.getElementById('unreadEmails');
const searchInput = document.getElementById('searchInput');
const emailLimit = document.getElementById('emailLimit');
const refreshBtn = document.getElementById('refreshBtn');
const logoutBtn = document.getElementById('logoutBtn');
const closeDetail = document.getElementById('closeDetail');

// Estado da aplicação
let currentEmails = [];
let currentFolderName = 'INBOX';
let isConnected = false;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupSocketListeners();
});

// Configuração dos event listeners
function setupEventListeners() {
    // Login
    loginForm.addEventListener('submit', handleLogin);
    
    // Interface de email
    refreshBtn.addEventListener('click', loadEmails);
    logoutBtn.addEventListener('click', handleLogout);
    closeDetail.addEventListener('click', closeEmailDetail);
    
    // Controles
    searchInput.addEventListener('input', handleSearch);
    emailLimit.addEventListener('change', loadEmails);
    
    // Clique em pastas
    document.addEventListener('click', function(e) {
        if (e.target.closest('.folder-item')) {
            const folderItem = e.target.closest('.folder-item');
            const folderName = folderItem.dataset.folder;
            selectFolder(folderName);
        }
        
        if (e.target.closest('.email-item')) {
            const emailItem = e.target.closest('.email-item');
            const emailId = emailItem.dataset.emailId;
            showEmailDetail(emailId);
        }
    });
}

// Configuração dos listeners do Socket.IO
function setupSocketListeners() {
    socket.on('connect', function() {
        console.log('Conectado ao servidor WebSocket');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Desconectado do servidor WebSocket');
        updateConnectionStatus(false);
    });
    
    socket.on('new_emails', function(data) {
        console.log('Novos emails recebidos:', data.emails);
        if (currentFolderName === 'INBOX') {
            updateEmailList(data.emails);
        }
    });
}

// Handlers
async function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(loginForm);
    const email = formData.get('email');
    const password = formData.get('password');
    
    showLoading(true);
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            showEmailInterface();
            loadFolders();
            loadEmails();
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        showNotification('Erro ao conectar. Tente novamente.', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleLogout() {
    try {
        const response = await fetch('/logout');
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            showLoginScreen();
            isConnected = false;
            updateConnectionStatus(false);
        }
    } catch (error) {
        console.error('Erro no logout:', error);
    }
}

async function loadEmails() {
    if (!isConnected) return;
    
    showLoading(true);
    
    try {
        const limit = emailLimit.value;
        const response = await fetch(`/emails?folder=${currentFolderName}&limit=${limit}`);
        const data = await response.json();
        
        if (data.success) {
            currentEmails = data.emails;
            updateEmailList(data.emails);
            updateStats(data.emails);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        console.error('Erro ao carregar emails:', error);
        showNotification('Erro ao carregar emails.', 'error');
    } finally {
        showLoading(false);
    }
}

async function loadFolders() {
    try {
        const response = await fetch('/folders');
        const data = await response.json();
        
        if (data.success) {
            updateFoldersList(data.folders);
        }
    } catch (error) {
        console.error('Erro ao carregar pastas:', error);
    }
}

function selectFolder(folderName) {
    currentFolderName = folderName;
    currentFolder.textContent = getFolderDisplayName(folderName);
    
    // Atualizar seleção visual
    document.querySelectorAll('.folder-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-folder="${folderName}"]`).classList.add('active');
    
    loadEmails();
}

function showEmailDetail(emailId) {
    const email = currentEmails.find(e => e.id === emailId);
    if (!email) return;
    
    document.getElementById('detailSubject').textContent = email.subject;
    document.getElementById('detailFrom').textContent = email.from;
    document.getElementById('detailDate').textContent = email.date;
    document.getElementById('detailBody').textContent = email.full_body;
    
    emailDetail.style.display = 'flex';
}

function closeEmailDetail() {
    emailDetail.style.display = 'none';
}

function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase();
    
    if (!searchTerm) {
        updateEmailList(currentEmails);
        return;
    }
    
    const filteredEmails = currentEmails.filter(email => 
        email.subject.toLowerCase().includes(searchTerm) ||
        email.from.toLowerCase().includes(searchTerm) ||
        email.body.toLowerCase().includes(searchTerm)
    );
    
    updateEmailList(filteredEmails);
}

// Funções de atualização da UI
function showLoginScreen() {
    loginScreen.style.display = 'flex';
    emailInterface.style.display = 'none';
    loginForm.reset();
}

function showEmailInterface() {
    loginScreen.style.display = 'none';
    emailInterface.style.display = 'flex';
    isConnected = true;
    updateConnectionStatus(true);
}

function updateEmailList(emails) {
    if (emails.length === 0) {
        emailList.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <h3>Nenhum email encontrado</h3>
                <p>Não há emails nesta pasta ou os critérios de busca não retornaram resultados.</p>
            </div>
        `;
        return;
    }
    
    emailList.innerHTML = emails.map(email => `
        <div class="email-item" data-email-id="${email.id}">
            <div class="email-header-info">
                <div class="email-subject">${escapeHtml(email.subject)}</div>
                <div class="email-date">${formatDate(email.date)}</div>
            </div>
            <div class="email-from">${escapeHtml(email.from)}</div>
            <div class="email-preview">${escapeHtml(email.body)}</div>
        </div>
    `).join('');
}

function updateFoldersList(folders) {
    const foldersList = document.getElementById('foldersList');
    
    // Manter a caixa de entrada sempre visível
    let html = `
        <li class="folder-item active" data-folder="INBOX">
            <i class="fas fa-inbox"></i> Caixa de Entrada
        </li>
    `;
    
    // Adicionar outras pastas
    folders.forEach(folder => {
        if (folder !== 'INBOX') {
            html += `
                <li class="folder-item" data-folder="${folder}">
                    <i class="fas fa-folder"></i> ${getFolderDisplayName(folder)}
                </li>
            `;
        }
    });
    
    foldersList.innerHTML = html;
}

function updateStats(emails) {
    totalEmails.textContent = emails.length;
    // Por simplicidade, consideramos todos como não lidos
    // Em uma implementação real, você verificaria o status de leitura
    unreadEmails.textContent = emails.length;
}

function updateConnectionStatus(connected) {
    if (connected) {
        connectionStatus.className = 'status-badge online';
        connectionStatus.innerHTML = '<i class="fas fa-circle"></i> Conectado';
    } else {
        connectionStatus.className = 'status-badge offline';
        connectionStatus.innerHTML = '<i class="fas fa-circle"></i> Desconectado';
    }
}

function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showNotification(message, type = 'info') {
    notification.className = `notification ${type}`;
    notificationMessage.textContent = message;
    notification.style.display = 'flex';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

// Funções utilitárias
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'Data desconhecida';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) {
            return 'Hoje';
        } else if (diffDays === 2) {
            return 'Ontem';
        } else if (diffDays <= 7) {
            return `${diffDays - 1} dias atrás`;
        } else {
            return date.toLocaleDateString('pt-BR');
        }
    } catch (error) {
        return dateString;
    }
}

function getFolderDisplayName(folderName) {
    const folderNames = {
        'INBOX': 'Caixa de Entrada',
        'SENT': 'Enviados',
        'DRAFT': 'Rascunhos',
        'TRASH': 'Lixeira',
        'SPAM': 'Spam',
        'JUNK': 'Spam'
    };
    
    return folderNames[folderName] || folderName;
}

// Atualização automática a cada 30 segundos
setInterval(() => {
    if (isConnected) {
        loadEmails();
    }
}, 30000);

// Atualização quando a janela ganha foco
window.addEventListener('focus', () => {
    if (isConnected) {
        loadEmails();
    }
});