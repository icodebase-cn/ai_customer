#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的主应用，用于排查问题
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="多语言智能客服", description="支持文字和图片输入的智能客服系统")

@app.get("/", response_class=HTMLResponse)
async def home():
    """主页"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>多语言智能客服</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .chat-container { max-width: 800px; margin: 0 auto; }
            .chat-box { border: 1px solid #ddd; padding: 20px; height: 400px; overflow-y: auto; }
            .input-area { margin-top: 20px; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h1>多语言智能客服系统</h1>
            <p>系统已启动，基本功能正常！</p>

            <div class="chat-box" id="chatBox">
                <p><strong>客服:</strong> 您好！我是多语言智能客服，有什么可以帮助您的吗？</p>
            </div>

            <div class="input-area">
                <input type="text" id="messageInput" placeholder="请输入您的问题...">
                <button onclick="sendMessage()">发送</button>
            </div>
        </div>

        <script>
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const chatBox = document.getElementById('chatBox');
                const message = input.value.trim();

                if (message) {
                    chatBox.innerHTML += '<p><strong>您:</strong> ' + message + '</p>';
                    chatBox.innerHTML += '<p><strong>客服:</strong> 感谢您的咨询！系统正在完善中，请稍后再试。</p>';
                    input.value = '';
                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            }

            // 回车发送
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """)

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "多语言智能客服", "version": "简化版"}

@app.get("/test")
async def test():
    """测试接口"""
    return {"message": "简化版主应用工作正常", "status": "ok"}

if __name__ == "__main__":
    print("🚀 启动简化版主应用...")
    uvicorn.run(app, host="0.0.0.0", port=8002)