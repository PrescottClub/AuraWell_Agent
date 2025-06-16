# AuraWell WebSocket 流式交互使用指南

## 概述

AuraWell Phase IV 引入了WebSocket流式交互功能，支持实时健康咨询和流式AI响应。

## 连接方式

### WebSocket 端点
```
ws://localhost:8000/ws/chat/{user_id}
```

### 前端 JavaScript 连接示例

```javascript
// 建立WebSocket连接
const userId = 'user_123';
const wsUrl = `ws://localhost:8000/ws/chat/${userId}`;
const socket = new WebSocket(wsUrl);

// 连接事件处理
socket.onopen = function(event) {
    console.log('WebSocket连接已建立');
};

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    handleMessage(message);
};

socket.onclose = function(event) {
    console.log('WebSocket连接已关闭');
};

socket.onerror = function(error) {
    console.error('WebSocket错误:', error);
};

// 消息处理函数
function handleMessage(message) {
    switch (message.type) {
        case 'welcome':
            console.log('欢迎消息:', message.message);
            break;
            
        case 'status_update':
            updateStatus(message.status, message.message);
            break;
            
        case 'chat_stream':
            appendStreamToken(message.delta);
            break;
            
        case 'error':
            handleError(message.message);
            break;
            
        default:
            console.log('未知消息类型:', message);
    }
}

// 发送健康咨询消息
function sendHealthChat(message, context = {}) {
    const chatMessage = {
        type: 'health_chat',
        data: {
            message: message,
            context: context
        },
        conversation_id: generateConversationId(),
        active_member_id: userId
    };
    
    socket.send(JSON.stringify(chatMessage));
}

// 发送一般聊天消息
function sendGeneralChat(message) {
    const chatMessage = {
        type: 'general_chat',
        data: {
            message: message
        },
        conversation_id: generateConversationId()
    };
    
    socket.send(JSON.stringify(chatMessage));
}

// 切换家庭成员
function switchMember(targetMemberId) {
    const switchMessage = {
        type: 'switch_member',
        data: {
            target_member_id: targetMemberId
        }
    };
    
    socket.send(JSON.stringify(switchMessage));
}

// 获取连接状态
function getStatus() {
    const statusMessage = {
        type: 'get_status',
        data: {}
    };
    
    socket.send(JSON.stringify(statusMessage));
}
```

## 消息格式

### 发送消息格式

#### 健康咨询消息
```json
{
  "type": "health_chat",
  "data": {
    "message": "我最近感觉很疲劳，有什么建议吗？",
    "context": {
      "mood": "tired",
      "sleep_hours": 6,
      "activity_level": "low"
    }
  },
  "conversation_id": "conv_123",
  "active_member_id": "user_123"
}
```

#### 一般聊天消息
```json
{
  "type": "general_chat",
  "data": {
    "message": "你好，今天天气怎么样？"
  },
  "conversation_id": "conv_123"
}
```

#### 切换家庭成员
```json
{
  "type": "switch_member",
  "data": {
    "target_member_id": "member_456"
  }
}
```

#### 获取状态
```json
{
  "type": "get_status",
  "data": {}
}
```

### 接收消息格式

#### 欢迎消息
```json
{
  "type": "welcome",
  "message": "欢迎使用AuraWell健康助手！",
  "user_id": "user_123",
  "connection_id": "conn_789",
  "timestamp": "2025-01-16T12:00:00Z"
}
```

#### 状态更新
```json
{
  "type": "status_update",
  "status": "streaming",
  "message": "正在生成个性化健康建议...",
  "timestamp": "2025-01-16T12:00:01Z"
}
```

#### 流式内容
```json
{
  "type": "chat_stream",
  "delta": "根据您的情况，我建议",
  "conversation_id": "conv_123",
  "timestamp": "2025-01-16T12:00:02Z"
}
```

#### 错误消息
```json
{
  "type": "error",
  "message": "处理您的请求时发生错误",
  "error_code": "PROCESSING_ERROR",
  "timestamp": "2025-01-16T12:00:03Z"
}
```

## 状态管理

WebSocket连接遵循以下状态流转：

```
连接建立 → sending → streaming → done
```

- **sending**: 正在发送请求到AI服务
- **streaming**: 正在接收AI响应流
- **done**: 响应完成

## 前端UI实现示例

### HTML结构
```html
<div id="chat-container">
    <div id="messages"></div>
    <div id="status-bar">
        <span id="connection-status">已连接</span>
        <span id="processing-status"></span>
    </div>
    <div id="input-area">
        <input type="text" id="message-input" placeholder="输入您的健康问题...">
        <button id="send-btn">发送</button>
    </div>
</div>
```

### JavaScript控制器
```javascript
class AuraWellChatController {
    constructor(userId) {
        this.userId = userId;
        this.socket = null;
        this.currentMessage = '';
        this.currentConversationId = null;
        
        this.initializeWebSocket();
        this.setupEventListeners();
    }
    
    initializeWebSocket() {
        const wsUrl = `ws://localhost:8000/ws/chat/${this.userId}`;
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            this.updateConnectionStatus('connected');
        };
        
        this.socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };
        
        this.socket.onclose = () => {
            this.updateConnectionStatus('disconnected');
        };
        
        this.socket.onerror = (error) => {
            this.updateConnectionStatus('error');
            console.error('WebSocket错误:', error);
        };
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'welcome':
                this.addSystemMessage(message.message);
                break;
                
            case 'status_update':
                this.updateProcessingStatus(message.status, message.message);
                if (message.status === 'streaming') {
                    this.startNewMessage();
                } else if (message.status === 'done') {
                    this.finishMessage();
                }
                break;
                
            case 'chat_stream':
                this.appendToCurrentMessage(message.delta);
                break;
                
            case 'error':
                this.addErrorMessage(message.message);
                break;
        }
    }
    
    sendHealthChat(message, context = {}) {
        this.currentConversationId = this.generateConversationId();
        
        const chatMessage = {
            type: 'health_chat',
            data: { message, context },
            conversation_id: this.currentConversationId,
            active_member_id: this.userId
        };
        
        this.socket.send(JSON.stringify(chatMessage));
        this.addUserMessage(message);
    }
    
    // UI更新方法
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        statusElement.textContent = status === 'connected' ? '已连接' : '连接断开';
        statusElement.className = status;
    }
    
    updateProcessingStatus(status, message) {
        const statusElement = document.getElementById('processing-status');
        statusElement.textContent = message;
        statusElement.className = status;
    }
    
    addUserMessage(message) {
        const messagesContainer = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.textContent = message;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    startNewMessage() {
        const messagesContainer = document.getElementById('messages');
        this.currentMessageElement = document.createElement('div');
        this.currentMessageElement.className = 'message assistant-message';
        messagesContainer.appendChild(this.currentMessageElement);
        this.currentMessage = '';
    }
    
    appendToCurrentMessage(delta) {
        this.currentMessage += delta;
        if (this.currentMessageElement) {
            this.currentMessageElement.textContent = this.currentMessage;
            
            // 自动滚动到底部
            const messagesContainer = document.getElementById('messages');
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    finishMessage() {
        this.currentMessageElement = null;
        this.updateProcessingStatus('', '');
    }
    
    generateConversationId() {
        return `conv_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
    }
}

// 初始化聊天控制器
const chatController = new AuraWellChatController('user_123');

// 设置发送按钮事件
document.getElementById('send-btn').addEventListener('click', () => {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    
    if (message) {
        chatController.sendHealthChat(message);
        input.value = '';
    }
});

// 设置回车键发送
document.getElementById('message-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        document.getElementById('send-btn').click();
    }
});
```

## CSS样式示例

```css
#chat-container {
    max-width: 800px;
    margin: 0 auto;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
}

#messages {
    height: 400px;
    overflow-y: auto;
    padding: 16px;
    background-color: #f9f9f9;
}

.message {
    margin-bottom: 12px;
    padding: 8px 12px;
    border-radius: 8px;
    max-width: 80%;
}

.user-message {
    background-color: #007bff;
    color: white;
    margin-left: auto;
    text-align: right;
}

.assistant-message {
    background-color: white;
    border: 1px solid #ddd;
    margin-right: auto;
}

.system-message {
    background-color: #ffeaa7;
    text-align: center;
    margin: 0 auto;
    font-style: italic;
}

.error-message {
    background-color: #ff7675;
    color: white;
    text-align: center;
    margin: 0 auto;
}

#status-bar {
    padding: 8px 16px;
    background-color: #f0f0f0;
    border-top: 1px solid #ddd;
    display: flex;
    justify-content: space-between;
    font-size: 14px;
}

#connection-status.connected {
    color: #00b894;
}

#connection-status.disconnected {
    color: #e17055;
}

#processing-status.streaming {
    color: #0984e3;
}

#input-area {
    padding: 16px;
    display: flex;
    gap: 8px;
}

#message-input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

#send-btn {
    padding: 8px 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

#send-btn:hover {
    background-color: #0056b3;
}

#send-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
}
```

## 注意事项

1. **认证**: WebSocket连接需要有效的用户ID
2. **错误处理**: 实现连接断开重连逻辑
3. **消息限制**: 单条消息建议不超过1000字符
4. **并发限制**: 单用户最多3个并发连接
5. **超时处理**: 长时间无响应会自动断开连接

## 测试方法

使用提供的测试脚本：

```bash
# 安装依赖
pip install websockets aiohttp

# 运行WebSocket测试
python test_websocket_phase_iv.py
```

## 性能指标

- 连接建立时间: < 100ms
- 首token响应时间: < 2s
- 流式响应延迟: < 50ms
- 并发连接支持: 100+

## 故障排除

### 常见问题

1. **连接失败**: 检查服务器是否运行在正确端口
2. **消息丢失**: 确认消息格式正确
3. **流式中断**: 检查网络连接稳定性
4. **响应超时**: 调整超时设置

### 调试技巧

```javascript
// 启用WebSocket调试日志
socket.addEventListener('message', (event) => {
    console.log('收到消息:', JSON.parse(event.data));
});

socket.addEventListener('error', (error) => {
    console.error('WebSocket错误:', error);
});
``` 