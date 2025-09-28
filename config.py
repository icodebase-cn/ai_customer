import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    # 配置
    AIQIANJI_API_KEY = os.getenv("AIQIANJI_API_KEY", "")
    AIQIANJI_BASE_URL = os.getenv("AIQIANJI_BASE_URL", "https://aiqianji.cn/v1")
    TEXT_MODEL = os.getenv("TEXT_MODEL", "")
    VISION_MODEL = os.getenv("VISION_MODEL", "")

    # 模型配置
    TEXT_MODEL = TEXT_MODEL  # 使用AI千集模型
    VISION_MODEL = VISION_MODEL  # AI千集模型也支持视觉功能
    EMBEDDING_MODEL = "text-embedding-ada-002"  # 保持原有嵌入模型

    # 知识库配置
    KNOWLEDGE_BASE_PATH = "knowledge_base"
    VECTOR_DB_PATH = "vector_db"

    # 图片处理配置
    MAX_IMAGE_SIZE = 1024 * 1024  # 1MB
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    # 系统配置
    MAX_TOKENS = 2000
    TEMPERATURE = 0.7

    # 电商知识库配置
    TAOBAO_KNOWLEDGE_URLS = [
        "https://raw.githubusercontent.com/your-repo/taobao-knowledge/main/faq.json",
        "https://raw.githubusercontent.com/your-repo/taobao-knowledge/main/products.json"
    ]