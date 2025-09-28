#!/usr/bin/env python3
"""
多语言智能客服系统启动脚本
"""

import os
import sys
import threading
import time
import webbrowser
from pathlib import Path

import requests
import uvicorn

from config import Config

sys.path.append(str(Path(__file__).parent))  # 确保当前目录在PYTHONPATH
from api.main import app  # 显式导入app


def open_browser():
    """等待系统完全启动后打开浏览器"""
    print("⏳ 等待系统完全启动...")

    # 增加等待时间，因为AI模型加载可能需要更长时间
    print("🔄 正在预加载AI模型和知识库，这可能需要几分钟...")
    time.sleep(15)  # 等待15秒
    # 检查服务器是否真的启动
    max_retries = 15  # 增加重试次数
    for i in range(max_retries):
        try:
            print(f"🔍 检查服务器状态... ({i+1}/{max_retries})")
            response = requests.get('http://localhost:8000/api/health', timeout=5)  # 增加超时时间
            if response.status_code == 200:
                print("✅ 系统启动完成！")
                break
        except requests.exceptions.ConnectionError:
            if i < max_retries - 1:
                print(f"⏳ 服务器尚未启动，继续等待... ({i+1}/{max_retries})")
                time.sleep(3)  # 增加等待间隔
            else:
                print("⚠️ 服务器启动超时，但仍尝试打开浏览器")
        except Exception as e:
            if i < max_retries - 1:
                print(f"⚠️ 连接检查失败: {e}，继续等待... ({i+1}/{max_retries})")
                time.sleep(3)
            else:
                print(f"❌ 连接检查最终失败: {e}")

    try:
        print("🌐 正在打开浏览器...")
        webbrowser.open('http://localhost:8000')
        print("✅ 浏览器已打开！系统完全准备就绪！")
        print("🎉 现在可以开始使用智能客服系统了！")
        print("💡 如果浏览器没有自动打开，请手动访问: http://localhost:8000")
    except Exception as e:
        print(f"⚠️ 自动打开浏览器失败: {e}")
        print("💡 请手动访问: http://localhost:8000")

def main():
    """主函数"""
    print("🚀 启动多语言智能客服系统...")

    # 检查API配置
    config = Config()
    print(f"✅ 使用AI千集模型: {config.TEXT_MODEL}")

    # 检查必要目录
    required_dirs = ["knowledge_base", "templates", "static"]
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)

    print("✅ 环境检查完成")
    print("🌐 启动Web服务器...")
    print("📝 注意：首次启动时AI模型加载可能需要几分钟，请耐心等待...")

    # 启动浏览器线程
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # 启动服务器
    uvicorn.run(
        app,  # 直接传app对象
        host="0.0.0.0",
        port=8000,
        reload=False,  # 关闭reload，避免多进程路径问题
        log_level="info"
    )

if __name__ == "__main__":
    main()