#!/usr/bin/env python3
"""
模型预加载脚本
在系统启动前预加载所有必要的模型和知识库
"""

import os
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

def preload_models():
    """预加载所有模型"""
    print("🚀 开始预加载模型和知识库...")
    print("=" * 60)

    total_start_time = time.time()

    try:
        # 1. 预加载配置
        print("📋 步骤1: 加载配置...")
        from config import Config
        config = Config()
        print(f"✅ 配置加载完成，使用模型: {config.TEXT_MODEL}")

        # 2. 预加载知识库
        print("\n📋 步骤2: 预加载知识库...")
        kb_start_time = time.time()
        from services.knowledge_base import KnowledgeBase

        kb = KnowledgeBase()
        kb.load_knowledge_base()

        kb_load_time = time.time() - kb_start_time
        print(f"✅ 知识库预加载完成！耗时: {kb_load_time:.2f}秒")
        print(f"📊 知识库条目数: {len(kb.documents)}")

        # 3. 预加载AI服务
        print("\n📋 步骤3: 预加载AI服务...")
        ai_start_time = time.time()
        from services.ai_service import AIService

        ai_service = AIService()

        ai_load_time = time.time() - ai_start_time
        print(f"✅ AI服务预加载完成！耗时: {ai_load_time:.2f}秒")

        # 4. 测试功能
        print("\n📋 步骤4: 功能测试...")
        test_start_time = time.time()

        # 测试知识库搜索
        search_results = kb.search("退款", top_k=3)
        print(f"✅ 知识库搜索测试: 找到 {len(search_results)} 个结果")

        # 测试AI响应
        response = ai_service.get_local_keyword_response("你好")
        print(f"✅ AI响应测试: {response[:50]}...")

        test_time = time.time() - test_start_time
        print(f"✅ 功能测试完成！耗时: {test_time:.2f}秒")

        # 5. 总结
        total_time = time.time() - total_start_time
        print("\n" + "=" * 60)
        print("🎉 模型预加载完成！")
        print(f"⏱️  总耗时: {total_time:.2f}秒")
        print(f"📚 知识库: {len(kb.documents)} 个条目")
        print(f"🤖 AI服务: 已就绪")
        print("✅ 系统准备就绪，可以启动Web服务！")

        return True

    except Exception as e:
        print(f"\n❌ 预加载失败: {e}")
        print("⚠️ 系统将继续运行，但某些功能可能不可用")
        return False

def main():
    """主函数"""
    print("🔧 多语言智能客服系统 - 模型预加载工具")
    print("=" * 60)

    # 检查必要目录
    required_dirs = ["knowledge_base", "templates", "static", "model_cache"]
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"📁 确保目录存在: {dir_name}")

    print()

    # 执行预加载
    success = preload_models()

    if success:
        print("\n💡 提示: 现在可以运行 'python run.py' 启动Web服务")
        return 0
    else:
        print("\n💡 提示: 预加载失败，但系统仍可运行，建议检查配置")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)