/**
 * Doctor-Patient Translation Web App - Frontend JavaScript
 * Handles UI interactions and REST API calls
 */

// ==================== Global State ====================

let currentConversationId = null;
let messageCount = 0;

// ==================== DOM Elements ====================

const elements = {
    newConversationBtn: document.getElementById('newConversationBtn'),
    summaryBtn: document.getElementById('summaryBtn'),
    conversationList: document.getElementById('conversationList'),
    conversationInfo: document.getElementById('conversationInfo'),
    currentConversationId: document.getElementById('currentConversationId'),
    messageCountSpan: document.getElementById('messageCount'),
    messagesContainer: document.getElementById('messagesContainer'),
    senderSelect: document.getElementById('senderSelect'),
    languageInput: document.getElementById('languageInput'),
    messageInput: document.getElementById('messageInput'),
    sendBtn: document.getElementById('sendBtn'),
    summaryPanel: document.getElementById('summaryPanel'),
    summaryContent: document.getElementById('summaryContent'),
    closeSummaryBtn: document.getElementById('closeSummaryBtn'),
    toast: document.getElementById('toast')
};

// ==================== API Functions ====================

/**
 * Create a new conversation
 */
async function createConversation() {
    try {
        const response = await fetch('/api/conversations', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentConversationId = data.conversation_id;
            updateUI();
            showToast('New conversation started!', 'success');
            await loadConversations();
            return true;
        } else {
            throw new Error(data.error || 'Failed to create conversation');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
        return false;
    }
}

/**
 * Load all conversations
 */
async function loadConversations() {
    try {
        const response = await fetch('/api/conversations');
        const data = await response.json();
        
        if (data.success) {
            const select = elements.conversationList;
            
            // Clear existing options except the first one
            select.innerHTML = '<option value="">-- No conversation selected --</option>';
            
            // Add conversation options
            data.conversations.forEach(conv => {
                const option = document.createElement('option');
                option.value = conv.id;
                const date = new Date(conv.created_at).toLocaleString();
                option.textContent = `Conversation #${conv.id} (${conv.message_count} messages) - ${date}`;
                
                if (conv.id === currentConversationId) {
                    option.selected = true;
                }
                
                select.appendChild(option);
            });
        }
    } catch (error) {
        showToast(`Error loading conversations: ${error.message}`, 'error');
    }
}

/**
 * Load messages for a conversation
 */
async function loadMessages(conversationId) {
    try {
        const response = await fetch(`/api/conversations/${conversationId}/messages`);
        const data = await response.json();
        
        if (data.success) {
            messageCount = data.messages.length;
            renderMessages(data.messages);
            updateUI();
        } else {
            throw new Error(data.error || 'Failed to load messages');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

/**
 * Send a new message
 */
async function sendMessage() {
    const sender = elements.senderSelect.value;
    const text = elements.messageInput.value.trim();
    const targetLanguage = elements.languageInput.value.trim() || 'English';
    
    if (!text) {
        showToast('Please enter a message', 'error');
        return;
    }
    
    if (!currentConversationId) {
        showToast('Please create a conversation first', 'error');
        return;
    }
    
    // Disable send button during request
    elements.sendBtn.disabled = true;
    elements.sendBtn.textContent = 'Sending...';
    
    try {
        const response = await fetch('/api/messages', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                sender: sender,
                text: text,
                target_language: targetLanguage
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Clear input
            elements.messageInput.value = '';
            
            // Reload messages
            await loadMessages(currentConversationId);
            
            showToast('Message sent!', 'success');
        } else {
            throw new Error(data.error || 'Failed to send message');
        }
    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        elements.sendBtn.disabled = false;
        elements.sendBtn.textContent = 'Send ➤';
    }
}

/**
 * Generate conversation summary
 */
async function generateSummary() {
    if (!currentConversationId) {
        showToast('No active conversation', 'error');
        return;
    }
    
    // Show summary panel with loading state
    elements.summaryPanel.classList.remove('hidden');
    elements.summaryContent.innerHTML = '<div class="loading">Generating summary...</div>';
    
    try {
        const response = await fetch(`/api/conversations/${currentConversationId}/summary`);
        const data = await response.json();
        
        if (data.success) {
            // Format summary with proper line breaks
            const formattedSummary = data.summary.replace(/\n/g, '<br>');
            elements.summaryContent.innerHTML = `<p>${formattedSummary}</p>`;
        } else {
            throw new Error(data.error || 'Failed to generate summary');
        }
    } catch (error) {
        elements.summaryContent.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        showToast(`Error: ${error.message}`, 'error');
    }
}

// ==================== UI Functions ====================

/**
 * Render messages in the chat area
 */
function renderMessages(messages) {
    const container = elements.messagesContainer;
    
    if (messages.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>👋 No messages yet. Start the conversation!</p></div>';
        return;
    }
    
    container.innerHTML = '';
    
    messages.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msg.sender}`;
        
        const date = new Date(msg.created_at).toLocaleTimeString();
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-badge">${msg.sender === 'doctor' ? '👨‍⚕️ Doctor' : '🧑 Patient'}</span>
                <span>${date}</span>
            </div>
            <div class="message-content">
                <div class="message-text">
                    <strong>Original:</strong>
                    <p>${escapeHtml(msg.original_text)}</p>
                </div>
                ${msg.translated_text ? `
                    <div class="message-translation">
                        <strong>Translation (${msg.language || 'English'}):</strong>
                        <p>${escapeHtml(msg.translated_text)}</p>
                    </div>
                ` : ''}
            </div>
        `;
        
        container.appendChild(messageDiv);
    });
    
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

/**
 * Update UI based on current state
 */
function updateUI() {
    if (currentConversationId) {
        elements.conversationInfo.classList.remove('hidden');
        elements.currentConversationId.textContent = currentConversationId;
        elements.messageCountSpan.textContent = messageCount;
        elements.sendBtn.disabled = false;
        elements.summaryBtn.disabled = messageCount === 0;
    } else {
        elements.conversationInfo.classList.add('hidden');
        elements.sendBtn.disabled = true;
        elements.summaryBtn.disabled = true;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = elements.toast;
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== Event Listeners ====================

// New conversation button
elements.newConversationBtn.addEventListener('click', async () => {
    await createConversation();
});

// Conversation selector
elements.conversationList.addEventListener('change', (e) => {
    const selectedId = parseInt(e.target.value);
    
    if (selectedId) {
        currentConversationId = selectedId;
        loadMessages(selectedId);
    } else {
        currentConversationId = null;
        elements.messagesContainer.innerHTML = '<div class="empty-state"><p>👋 Start a new conversation to begin</p></div>';
        messageCount = 0;
        updateUI();
    }
});

// Send message button
elements.sendBtn.addEventListener('click', () => {
    sendMessage();
});

// Send message on Enter (Shift+Enter for new line)
elements.messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Generate summary button
elements.summaryBtn.addEventListener('click', () => {
    generateSummary();
});

// Close summary panel
elements.closeSummaryBtn.addEventListener('click', () => {
    elements.summaryPanel.classList.add('hidden');
});

// ==================== Initialization ====================

/**
 * Initialize the application
 */
async function init() {
    console.log('🏥 Doctor-Patient Translation App initialized');
    
    // Load existing conversations
    await loadConversations();
    
    // Update UI
    updateUI();
}

// Run initialization when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
