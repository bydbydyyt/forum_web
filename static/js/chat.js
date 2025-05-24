document.addEventListener('DOMContentLoaded', function() {
    const chatSocket = new WebSocket(
        'ws://' + window.location.host + '/ws/chat/' + roomName + '/'
    );

    const messagesContainer = document.querySelector('.chat-messages');
    const messageInput = document.querySelector('#messageInput');
    const sendButton = document.querySelector('#sendButton');
    const fileInput = document.querySelector('#fileInput');
    const typingIndicator = document.querySelector('.typing-indicator');
    let typingTimeout;

    // WebSocket连接建立
    chatSocket.onopen = function(e) {
        console.log('WebSocket连接已建立');
    };

    // 接收消息
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        
        if (data.type === 'chat_message') {
            appendMessage(data);
        } else if (data.type === 'typing') {
            handleTypingIndicator(data);
        }
    };

    // WebSocket连接关闭
    chatSocket.onclose = function(e) {
        console.error('WebSocket连接已关闭');
    };

    // 发送消息
    function sendMessage(message, messageType = 'text', fileUrl = '') {
        chatSocket.send(JSON.stringify({
            'type': 'chat_message',
            'message': message,
            'message_type': messageType,
            'file_url': fileUrl
        }));
    }

    // 添加消息到聊天界面
    function appendMessage(data) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${data.is_sent ? 'sent' : 'received'}`;
        
        let content = '';
        if (data.message_type === 'text') {
            content = `<div class="message-content">${data.message}</div>`;
        } else if (data.message_type === 'image') {
            content = `
                <div class="message-content">
                    <div class="file-preview">
                        <img src="${data.file_url}" alt="图片">
                    </div>
                </div>
            `;
        } else if (data.message_type === 'video') {
            content = `
                <div class="message-content">
                    <div class="file-preview">
                        <video controls>
                            <source src="${data.file_url}" type="video/mp4">
                        </video>
                    </div>
                </div>
            `;
        } else if (data.message_type === 'file') {
            content = `
                <div class="message-content">
                    <div class="file-item">
                        <i class="file-icon">📎</i>
                        <a href="${data.file_url}" target="_blank">${data.message}</a>
                    </div>
                </div>
            `;
        }
        
        messageDiv.innerHTML = content + `
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // 处理正在输入提示
    function handleTypingIndicator(data) {
        if (data.is_typing) {
            typingIndicator.textContent = `${data.sender}正在输入...`;
            typingIndicator.style.display = 'block';
        } else {
            typingIndicator.style.display = 'none';
        }
    }

    // 发送按钮点击事件
    sendButton.onclick = function() {
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
            messageInput.value = '';
        }
    };

    // 输入框回车事件
    messageInput.onkeypress = function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    };

    // 输入框输入事件
    messageInput.oninput = function() {
        clearTimeout(typingTimeout);
        chatSocket.send(JSON.stringify({
            'type': 'typing',
            'is_typing': true
        }));
        
        typingTimeout = setTimeout(() => {
            chatSocket.send(JSON.stringify({
                'type': 'typing',
                'is_typing': false
            }));
        }, 1000);
    };

    // 文件上传处理
    fileInput.onchange = function(e) {
        const files = e.target.files;
        if (files.length > 0) {
            const formData = new FormData();
            for (let file of files) {
                formData.append('files', file);
            }
            
            fetch('{% url "chat:upload_file" chat_user.username %}', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    for (let file of data.files) {
                        sendMessage(file.name, file.type, file.url);
                    }
                }
            });
        }
    };

    // 移动端侧边栏切换
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.onclick = function() {
            const sidebar = document.querySelector('.chat-sidebar');
            sidebar.classList.toggle('show');
        };
    }
}); 