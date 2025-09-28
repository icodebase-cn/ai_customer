#!/usr/bin/env python3
"""
多语言智能客服系统快速启动脚本
跳过AI模型预加载，只启动基本Web服务器
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

import uvicorn

sys.path.append(str(Path(__file__).parent))

def create_minimal_app():
    """创建最小化的FastAPI应用，跳过AI模型预加载"""
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, Response
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates

    app = FastAPI(title="多语言智能客服 - 快速模式", description="快速启动模式，AI功能暂不可用")

    # 创建必要的目录
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)

    # 挂载静态文件
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # 模板配置
    templates = Jinja2Templates(directory="templates")

    @app.get("/favicon.ico")
    async def favicon():
        """返回favicon图标"""
        # 返回一个简单的空响应，避免404错误
        return Response(status_code=204)

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """主页"""
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except Exception as e:
            return HTMLResponse(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>多语言智能客服 - 快速模式</title>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .warning {{ color: orange; font-weight: bold; }}
                    .success {{ color: green; }}
                </style>
            </head>
            <body>
                <h1>多语言智能客服系统</h1>
                <p class="success">✅ 系统已启动（快速模式）</p>
                <p class="warning">⚠️ AI功能暂不可用，正在后台加载中...</p>
                <p>💡 建议等待几分钟后刷新页面，或使用完整启动模式</p>
                <p><a href="/docs">查看API文档</a></p>
                <p><a href="/api/health">健康检查</a></p>
                <p><a href="/api/status">系统状态</a></p>
            </body>
            </html>
            """)

    @app.get("/api/health")
    async def health_check():
        """健康检查"""
        return {"status": "healthy", "mode": "quick_start", "ai_ready": False}

    @app.get("/api/status")
    async def status_check():
        """系统状态检查"""
        return {
            "status": "running",
            "mode": "quick_start",
            "ai_ready": False,
            "message": "系统正在后台加载AI模型，请稍后重试"
        }

    @app.post("/api/chat")
    async def chat():
        """聊天接口（快速模式下不可用）"""
        return {
            "success": False,
            "error": "AI服务正在加载中，请稍后重试",
            "mode": "quick_start"
        }

    return app

def open_browser():
    """等待服务器启动后打开浏览器"""
    print("⏳ 等待服务器启动...")
    time.sleep(3)  # 快速启动只需要等待3秒

    import requests
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get('http://localhost:8000/api/health', timeout=2)
            if response.status_code == 200:
                print("✅ 服务器启动完成！")
                break
        except:
            if i < max_retries - 1:
                print(f"⏳ 等待服务器启动... ({i+1}/{max_retries})")
                time.sleep(1)
            else:
                print("⚠️ 服务器启动检查失败，但仍尝试打开浏览器")

    try:
        print("🌐 正在打开浏览器...")
        webbrowser.open('http://localhost:8000')
        print("✅ 浏览器已打开！")
        print("💡 注意：这是快速启动模式，AI功能正在后台加载中...")
    except Exception as e:
        print(f"⚠️ 自动打开浏览器失败: {e}")
        print("💡 请手动访问: http://localhost:8000")

def main():
    """主函数"""
    print("🚀 启动多语言智能客服系统（快速模式）...")
    print("⚡ 跳过AI模型预加载，快速启动Web服务器")

    # 检查必要目录
    required_dirs = ["knowledge_base", "templates", "static"]
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)

    print("✅ 环境检查完成")
    print("🌐 启动Web服务器...")

    # 启动浏览器线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # 创建并启动最小化应用
    app = create_minimal_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()