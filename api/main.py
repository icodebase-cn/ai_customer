import os
import time
from typing import Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import Config
from services.ai_service import AIService

app = FastAPI(title="多语言智能客服", description="支持文字和图片输入的智能客服系统")

# 创建必要的目录
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 模板配置
templates = Jinja2Templates(directory="templates")

# 全局AI服务实例
ai_service = None

@app.on_event("startup")
async def startup_event():
    """应用启动时预加载AI服务和知识库"""
    global ai_service
    print("🚀 系统启动中，正在预加载AI模型和知识库...")

    try:
        print("📚 正在加载知识库...")
        start_time = time.time()

        # 预加载AI服务
        print("🤖 初始化AI服务...")
        ai_service = AIService()

        # 预加载知识库
        print("📖 加载知识库数据...")
        ai_service.knowledge_base.load_knowledge_base()

        load_time = time.time() - start_time
        print(f"✅ AI模型和知识库预加载完成！耗时: {load_time:.2f}秒")
        print(f"📊 知识库条目数: {len(ai_service.knowledge_base.documents)}")
        print("🌐 Web服务器已准备就绪！")

    except Exception as e:
        print(f"❌ AI服务预加载失败: {e}")
        print("⚠️ 系统将继续运行，但AI功能可能不可用")
        print("💡 请检查网络连接和API配置")
        ai_service = None

def get_ai_service():
    """获取AI服务实例"""
    global ai_service
    if ai_service is None:
        print("⚠️ AI服务未初始化，尝试重新初始化...")
        try:
            ai_service = AIService()
        except Exception as e:
            print(f"❌ AI服务初始化失败: {e}")
            return None
    return ai_service

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
        # 如果模板加载失败，返回简单的HTML
        return HTMLResponse(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>多语言智能客服</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>多语言智能客服系统</h1>
            <p>系统已启动，但模板加载失败: {e}</p>
            <p><a href="/docs">查看API文档</a></p>
            <p><a href="/api/health">健康检查</a></p>
        </body>
        </html>
        """)

@app.post("/api/chat")
async def chat(
    message: str = Form(...),
    image: Optional[UploadFile] = File(None),
    language: str = Form('zh'),
    user_info: Optional[str] = Form(None)
):
    """处理聊天请求"""
    try:
        # 处理图片上传
        image_data = None
        if image and image.content_type:
            # 验证图片格式
            if not image.content_type.startswith('image/'):
                print(f"❌ 不支持的图片类型: {image.content_type}")
                raise HTTPException(
                    status_code=400,
                    detail=f"只支持以下图片格式: {', '.join(Config.SUPPORTED_IMAGE_FORMATS)}"
                )

            # 读取图片数据
            image_data = await image.read()
            print(f"📊 图片大小: {len(image_data)/1024:.2f}KB")

            # 验证图片大小
            if len(image_data) > Config.MAX_IMAGE_SIZE:
                print(f"❌ 图片大小超过限制: {len(image_data)} > {Config.MAX_IMAGE_SIZE}")
                raise HTTPException(
                    status_code=400,
                    detail=f"图片文件过大 (最大 {Config.MAX_IMAGE_SIZE/1024/1024:.1f}MB)"
                )

        # 调用AI服务
        service = get_ai_service()
        if service is None:
            raise HTTPException(status_code=500, detail="AI服务未初始化")

        # 检测消息语言，如果与当前语言设置不一致则更新
        if message and message.strip():
            try:
                detected_lang = service.detect_language(message)
                if detected_lang and detected_lang != language:
                    print(f"检测到语言变化: {language} -> {detected_lang}")
                    language = detected_lang
            except Exception as e:
                print(f"语言检测失败: {e}，继续使用原语言设置: {language}")

        # 使用异步获取增强响应
        response = await service.get_enhanced_response(
            user_question=message,
            image_data=image_data,
            lang=language,
            user_info=user_info
        )
        # 添加语言标识到响应中，供前端更新页面语言
        response['lang'] = language
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/knowledge/add")
async def add_knowledge(
    question: str = Form(...),
    answer: str = Form(...),
    category: str = Form("custom")
):
    """添加知识到知识库"""
    try:
        service = get_ai_service()
        if service is None:
            raise HTTPException(status_code=500, detail="AI服务未初始化")

        result = service.add_to_knowledge_base(question, answer, category)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/knowledge/search")
async def search_knowledge(query: str, top_k: int = 5):
    """搜索知识库"""
    try:
        service = get_ai_service()
        if service is None:
            raise HTTPException(status_code=500, detail="AI服务未初始化")

        result = service.search_knowledge_base(query, top_k)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/clear")
async def clear_chat_history():
    """清空对话历史"""
    try:
        service = get_ai_service()
        if service is None:
            raise HTTPException(status_code=500, detail="AI服务未初始化")

        # 清空对话历史
        service.clear_conversation_history()

        return {"status": "success", "message": "对话历史已清空"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/update-settings")
async def update_settings(
    apiKey: str,
    apiUrl: str
):
    """更新API设置"""
    try:
        # 更新配置
        Config.AIQIANJI_API_KEY = apiKey
        Config.AIQIANJI_BASE_URL = apiUrl

        # 如果AI服务已初始化，重新初始化以应用新配置
        global ai_service
        if ai_service:
            print("🔄 重新初始化AI服务以应用新配置...")
            ai_service = AIService()

        return {"status": "success", "message": "API设置已更新"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "多语言智能客服"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)