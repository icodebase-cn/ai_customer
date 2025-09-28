#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动下载模型脚本
"""

import os
import time
from sentence_transformers import SentenceTransformer

def download_model():
    """下载模型到本地缓存"""
    print("🚀 开始下载文本向量化模型...")
    print("📦 模型名称: paraphrase-multilingual-MiniLM-L12-v2")
    print("⏳ 请确保VPN连接正常...")
    
    # 设置缓存目录
    cache_dir = os.path.join(os.getcwd(), 'model_cache')
    os.makedirs(cache_dir, exist_ok=True)
    
    # 设置环境变量
    os.environ['TRANSFORMERS_CACHE'] = cache_dir
    os.environ['HF_HOME'] = cache_dir
    os.environ['HF_HUB_DOWNLOAD_TIMEOUT'] = '600'  # 10分钟超时
    
    try:
        start_time = time.time()
        
        print("🔄 正在下载模型文件...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        end_time = time.time()
        download_time = end_time - start_time
        
        print(f"✅ 模型下载成功！")
        print(f"⏱️ 下载耗时: {download_time:.2f}秒")
        print(f"📁 缓存位置: {os.path.abspath(cache_dir)}")
        
        # 测试模型
        print("🧪 测试模型功能...")
        test_texts = ["你好", "这是一个测试"]
        embeddings = model.encode(test_texts)
        print(f"✅ 模型测试成功！生成向量维度: {embeddings.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型下载失败: {e}")
        print("💡 请检查：")
        print("   1. VPN连接是否正常")
        print("   2. 网络连接是否稳定")
        print("   3. 磁盘空间是否充足")
        return False

def check_model_cache():
    """检查模型缓存"""
    cache_dir = os.path.join(os.getcwd(), 'model_cache')
    if os.path.exists(cache_dir):
        print(f"📁 发现模型缓存目录: {cache_dir}")
        files = os.listdir(cache_dir)
        print(f"📄 缓存文件数量: {len(files)}")
        return True
    else:
        print("❌ 未发现模型缓存目录")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🤖 文本向量化模型下载工具")
    print("=" * 50)
    
    # 检查现有缓存
    if check_model_cache():
        print("💡 发现现有缓存，可以尝试直接使用")
    
    print("\n🚀 开始下载模型...")
    print("⚠️ 请确保VPN连接正常！")
    
    success = download_model()
    
    if success:
        print("\n🎉 模型下载完成！")
        print("💡 现在可以启动系统了：python run.py")
    else:
        print("\n❌ 模型下载失败")
        print("💡 请检查网络连接后重试")

if __name__ == "__main__":
    main() 