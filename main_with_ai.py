#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带AI功能的主应用
"""

import json

import uvicorn
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="多语言智能客服", description="支持文字和图片输入的智能客服系统")

# 简单的AI回复逻辑
def get_ai_response(message):
    """简单的AI回复逻辑"""
    message_lower = message.lower()

    # 关键词匹配
    if "你好" in message or "您好" in message:
        return "您好！我是多语言智能客服，很高兴为您服务！请问有什么可以帮助您的吗？"

    elif "退款" in message or "退货" in message:
        return "关于退款/退货，您可以：1. 在订单页面申请退款 2. 联系卖家协商 3. 如果卖家不同意，可以申请平台介入。请问您需要具体帮助吗？"

    elif "物流" in message or "快递" in message or "发货" in message:
        return "关于物流问题：1. 您可以在订单页面查看物流信息 2. 如果长时间未发货，可以联系卖家 3. 如果物流异常，可以联系快递公司。请问您遇到什么具体问题？"

    elif "价格" in message or "优惠" in message or "便宜" in message:
        return "关于价格优惠：1. 关注店铺优惠券 2. 参与平台活动 3. 使用积分抵扣 4. 等待促销活动。请问您想了解哪种优惠方式？"

    elif "推荐" in message or "建议" in message:
        return "我可以根据您的需求推荐商品，请告诉我：1. 您想买什么类型的商品？2. 您的预算范围？3. 有什么特殊要求吗？"

    else:
        return "感谢您的咨询！我是多语言智能客服，可以帮您解答：退款退货、物流配送、价格优惠、商品推荐等问题。请问您需要什么帮助？"

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
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .chat-container { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .header { background: #007bff; color: white; padding: 20px; border-radius: 10px 10px 0 0; }
            .chat-box { padding: 20px; height: 400px; overflow-y: auto; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user-message { background: #e3f2fd; text-align: right; }
            .bot-message { background: #f5f5f5; }
            .input-area { padding: 20px; border-top: 1px solid #eee; }
            input[type="text"] { width: 70%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="header">
                <h1>多语言智能客服系统</h1>
                <p>智能AI助手，为您提供专业服务</p>
            </div>

            <div class="chat-box" id="chatBox">
                <div class="message bot-message">
                    <strong>智能客服:</strong> 您好！我是多语言智能客服，有什么可以帮助您的吗？
                </div>
            </div>

            <div class="input-area">
                <input type="text" id="messageInput" placeholder="请输入您的问题..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">发送</button>
            </div>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('messageInput');
                const chatBox = document.getElementById('chatBox');
                const message = input.value.trim();

                if (message) {
                    // 添加用户消息
                    chatBox.innerHTML += '<div class="message user-message"><strong>您:</strong> ' + message + '</div>';
                    input.value = '';
                    chatBox.scrollTop = chatBox.scrollHeight;

                    // 发送到后端获取AI回复
                    try {
                        const response = await fetch('/api/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/x-www-form-urlencoded',
                            },
                            body: 'message=' + encodeURIComponent(message)
                        });

                        const data = await response.json();
                        const aiReply = data.answer || '抱歉，我现在无法回答您的问题。';

                        // 添加AI回复
                        chatBox.innerHTML += '<div class="message bot-message"><strong>智能客服:</strong> ' + aiReply + '</div>';
                    } catch (error) {
                        chatBox.innerHTML += '<div class="message bot-message"><strong>智能客服:</strong> 抱歉，网络连接出现问题，请稍后再试。</div>';
                    }

                    chatBox.scrollTop = chatBox.scrollHeight;
                }
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """)

@app.post("/api/chat")
async def chat(message: str = Form(...)):
    """处理聊天请求"""
    try:
        ai_response = get_ai_response(message)
        return {
            "success": True,
            "answer": ai_response,
            "message": message
        }
    except Exception as e:
        return {
            "success": False,
            "answer": "抱歉，处理您的问题时出现了错误。",
            "error": str(e)
        }

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "多语言智能客服", "version": "AI增强版"}

if __name__ == "__main__":
    print("🚀 启动AI增强版主应用...")
    uvicorn.run(app, host="0.0.0.0", port=8003)