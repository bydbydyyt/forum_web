// 全局变量
const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
const csrfToken = csrfTokenElement ? csrfTokenElement.value : '';

// 工具函数
function formatDate(dateString) {
    // 检查输入是否有效
    if (!dateString) {
        return '刚刚';
    }
    
    const date = new Date(dateString);
    
    // 检查日期是否有效
    if (isNaN(date.getTime())) {
        return '刚刚';
    }
    
    const now = new Date();
    const diff = now - date;
    
    // 小于1分钟
    if (diff < 60000) {
        return '刚刚';
    }
    // 小于1小时
    if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}分钟前`;
    }
    // 小于24小时
    if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}小时前`;
    }
    // 小于30天
    if (diff < 2592000000) {
        return `${Math.floor(diff / 86400000)}天前`;
    }
    
    return date.toLocaleDateString();
}

// 消息提示
function showMessage(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main .container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // 3秒后自动消失
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// 图片预览
function setupImagePreview(input, previewElement) {
    input.addEventListener('change', function() {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewElement.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
}

// 无限滚动
function setupInfiniteScroll(container, loadMore) {
    let loading = false;
    let page = 1;
    
    container.addEventListener('scroll', function() {
        if (loading) return;
        
        const {scrollTop, scrollHeight, clientHeight} = container;
        if (scrollTop + clientHeight >= scrollHeight - 100) {
            loading = true;
            page++;
            
            loadMore(page).then(() => {
                loading = false;
            }).catch(() => {
                loading = false;
            });
        }
    });
}

// WebSocket连接
class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.socket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }
    
    connect() {
        this.socket = new WebSocket(this.url);
        
        this.socket.onopen = () => {
            console.log('WebSocket连接已建立');
            this.reconnectAttempts = 0;
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket连接已关闭');
            this.reconnect();
        };
        
        this.socket.onerror = (error) => {
            console.error('WebSocket错误:', error);
        };
        
        this.socket.onmessage = (event) => {
            this.handleMessage(event.data);
        };
    }
    
    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`尝试重新连接... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connect();
            }, this.reconnectDelay * this.reconnectAttempts);
        }
    }
    
    send(data) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }
    
    handleMessage(data) {
        try {
            const message = JSON.parse(data);
            // 处理不同类型的消息
            switch (message.type) {
                case 'chat_message':
                    this.handleChatMessage(message);
                    break;
                case 'notification':
                    this.handleNotification(message);
                    break;
                default:
                    console.log('未知消息类型:', message);
            }
        } catch (error) {
            console.error('消息处理错误:', error);
        }
    }
    
    handleChatMessage(message) {
        // 在聊天界面添加新消息
        // 检查是否在聊天页面，如果是则跳过处理（由chat.html中的appendMessage处理）
        if (window.location.pathname.includes('/chat/') && window.location.pathname !== '/chat/') {
            return; // 在具体聊天页面时不处理，避免重复显示
        }
        
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            const messageElement = document.createElement('div');
            messageElement.className = `message ${message.is_sent ? 'message-sent' : 'message-received'} fade-in`;
            messageElement.innerHTML = `
                <div class="message-content">
                    <div class="message-text">${message.message}</div>
                    <div class="message-time">${formatDate(message.created_at)}</div>
                </div>
            `;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
    
    handleNotification(message) {
        // 显示通知
        showMessage(message.content, message.type);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化图片预览
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(input => {
        const preview = input.nextElementSibling;
        if (preview && preview.tagName === 'IMG') {
            setupImagePreview(input, preview);
        }
    });
    
    // 只在聊天页面初始化WebSocket连接
    if (window.location.pathname.startsWith('/chat/') && window.location.pathname !== '/chat/') {
        // 从URL中提取用户名
        const pathParts = window.location.pathname.split('/');
        const chatUsername = pathParts[pathParts.length - 2]; // 获取倒数第二个部分作为用户名
        
        // 获取当前用户名（从页面中获取）
        const currentUserElement = document.querySelector('[data-current-user]');
        const currentUsername = currentUserElement ? currentUserElement.dataset.currentUser : null;
        
        if (chatUsername && currentUsername) {
            // 生成聊天室名称（与后端逻辑保持一致）
            const roomName = [currentUsername, chatUsername].sort().join('_');
            const wsUrl = `ws://${window.location.host}/ws/chat/${roomName}/`;
            const wsClient = new WebSocketClient(wsUrl);
            wsClient.connect();
        }
    }
    
    // 初始化无限滚动
    const scrollContainers = document.querySelectorAll('.infinite-scroll');
    scrollContainers.forEach(container => {
        setupInfiniteScroll(container, async (page) => {
            // 实现加载更多内容的逻辑
            const response = await fetch(`/api/posts/?page=${page}`);
            const data = await response.json();
            // 添加新内容到容器
            // ...
        });
    });
});