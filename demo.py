#!/usr/bin/env python3
"""
多语言智能客服系统演示脚本
"""

import json
from pathlib import Path


def demo_knowledge_base():
    """演示知识库功能"""
    print("📚 知识库演示")
    print("=" * 50)

    # 加载FAQ知识库
    faq_path = Path("knowledge_base/product_faq.json")
    if faq_path.exists():
        with open(faq_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)

        print(f"FAQ知识库包含 {len(faq_data.get('faqs', []))} 个问题")
        print("\n示例问题:")
        for i, faq in enumerate(faq_data.get('faqs', [])[:3]):
            print(f"{i+1}. {faq['question']}")
            print(f"   答案: {faq['answer'][:100]}...")
            print()

    # 加载商品分类知识库
    category_path = Path("knowledge_base/product_categories.json")
    if category_path.exists():
        with open(category_path, 'r', encoding='utf-8') as f:
            category_data = json.load(f)

        print(f"商品分类知识库包含 {len(category_data.get('categories', []))} 个主分类")
        print("\n商品分类:")
        for category in category_data.get('categories', []):
            print(f"• {category['name']}")
            for subcategory in category.get('subcategories', []):
                print(f"  - {subcategory['name']}")

def demo_prompts():
    """演示提示词系统"""
    print("\n🎯 提示词系统演示")
    print("=" * 50)

    try:
        from prompts.chinese_prompts import ChinesePrompts

        # 演示不同类型的提示词
        prompt_types = [
            ("text_chat", "如何申请退款？", "退款相关FAQ内容"),
            ("image_analysis", "这个商品怎么样？", "用户上传的商品图片"),
            ("after_sales", "商品有质量问题", "质量问题"),
            ("logistics_query", "什么时候发货", "物流查询"),
            ("price_discount", "有优惠吗", "价格优惠")
        ]

        for prompt_type, question, context in prompt_types:
            try:
                prompt = ChinesePrompts.get_prompt_by_type(
                    prompt_type,
                    user_question=question,
                    knowledge_context=context,
                    image_description=context if "image" in prompt_type else "",
                    issue_description=context if "after_sales" in prompt_type else "",
                    logistics_query=context if "logistics" in prompt_type else "",
                    price_query=context if "price" in prompt_type else ""
                )
                print(f"✅ {prompt_type}: 提示词生成成功 ({len(prompt)} 字符)")
            except Exception as e:
                print(f"❌ {prompt_type}: 提示词生成失败 - {e}")

    except ImportError:
        print("❌ 提示词模块导入失败")

def demo_config():
    """演示配置系统"""
    print("\n⚙️ 配置系统演示")
    print("=" * 50)

    try:
        from config import Config

        config = Config()

        print("系统配置:")
        print(f"• 文本模型: {config.TEXT_MODEL}")
        print(f"• 视觉模型: {config.VISION_MODEL}")
        print(f"• 嵌入模型: {config.EMBEDDING_MODEL}")
        print(f"• 最大Token: {config.MAX_TOKENS}")
        print(f"• 温度设置: {config.TEMPERATURE}")
        print(f"• 知识库路径: {config.KNOWLEDGE_BASE_PATH}")
        print(f"• 向量数据库路径: {config.VECTOR_DB_PATH}")
        print(f"• 最大图片大小: {config.MAX_IMAGE_SIZE / 1024 / 1024:.1f}MB")
        print(f"• 支持图片格式: {', '.join(config.SUPPORTED_IMAGE_FORMATS)}")

    except ImportError:
        print("❌ 配置模块导入失败")

def demo_web_interface():
    """演示Web界面功能"""
    print("\n🌐 Web界面演示")
    print("=" * 50)

    print("Web界面功能:")
    print("• 现代化响应式设计")
    print("• 实时聊天界面")
    print("• 图片上传和预览")
    print("• 快速问题按钮")
    print("• 移动端友好")
    print("• 加载动画效果")
    print("• 自动滚动到最新消息")

    print("\n技术特点:")
    print("• 使用Tailwind CSS框架")
    print("• Font Awesome图标")
    print("• 原生JavaScript交互")
    print("• 异步API调用")
    print("• 表单验证")

def demo_api_endpoints():
    """演示API接口"""
    print("\n🔌 API接口演示")
    print("=" * 50)

    print("主要API接口:")
    print("• POST /api/chat - 处理文字和图片聊天")
    print("• POST /api/knowledge/add - 添加知识到知识库")
    print("• GET /api/knowledge/search - 搜索知识库")
    print("• GET /api/health - 服务状态检查")

    print("\n请求示例:")
    print("文字聊天:")
    print("curl -X POST 'http://localhost:8000/api/chat' \\")
    print("  -F 'message=如何申请退款？'")

    print("\n图片聊天:")
    print("curl -X POST 'http://localhost:8000/api/chat' \\")
    print("  -F 'message=这个商品怎么样？' \\")
    print("  -F 'image=@product.jpg'")

def main():
    """主演示函数"""
    print("🎉 多语言智能客服系统演示")
    print("=" * 60)

    demos = [
        demo_knowledge_base,
        demo_prompts,
        demo_config,
        demo_web_interface,
        demo_api_endpoints
    ]

    for demo in demos:
        try:
            demo()
        except Exception as e:
            print(f"❌ 演示失败: {e}")

        print("\n" + "-" * 60 + "\n")

    print("🚀 启动说明:")
    print("1. 确保已安装所有依赖: pip install -r requirements.txt")
    print("2. 设置OpenAI API密钥: 创建.env文件")
    print("3. 运行系统: python run.py")
    print("4. 访问Web界面: http://localhost:8000")

    print("\n💡 使用提示:")
    print("• 支持文字和图片输入")
    print("• 可以询问退款、物流、售后等问题")
    print("• 上传商品图片进行分析")
    print("• 点击快速问题按钮测试功能")

if __name__ == "__main__":
    main()