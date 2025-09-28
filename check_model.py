#!/usr/bin/env python3
"""
模型状态检查脚本
快速检查AI模型是否已正确下载和可用
"""

import os
import sys

def check_model_status():
    """检查模型状态"""
    print("🔍 检查AI模型状态...")
    
    # 检查模型文件是否存在
    model_path = r"C:\Users\Lenovo\.cache\huggingface\hub\models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2\snapshots\86741b4e3f5cb7765a600d3a3d55a0f6a6cb443d"
    
    if os.path.exists(model_path):
        print("✅ 模型文件存在")
        
        # 检查关键文件
        key_files = ['model.safetensors', 'config.json', 'tokenizer.json']
        missing_files = []
        
        for file in key_files:
            file_path = os.path.join(model_path, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"✅ {file} - {size:,} bytes")
            else:
                missing_files.append(file)
                print(f"❌ {file} - 缺失")
        
        if missing_files:
            print(f"\n⚠️ 缺少文件: {', '.join(missing_files)}")
            return False
        else:
            print("\n✅ 所有模型文件完整")
            return True
    else:
        print("❌ 模型文件不存在")
        return False

def test_model_loading():
    """测试模型加载"""
    print("\n🧪 测试模型加载...")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # 设置环境变量
        os.environ['HF_HUB_OFFLINE'] = '1'
        
        model_path = r"C:\Users\Lenovo\.cache\huggingface\hub\models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2\snapshots\86741b4e3f5cb7765a600d3a3d55a0f6a6cb443d"
        
        if os.path.exists(model_path):
            model = SentenceTransformer(model_path)
            print("✅ 模型加载成功")
            
            # 简单测试
            test_text = ["测试文本"]
            embeddings = model.encode(test_text)
            print(f"✅ 模型功能正常，向量维度: {embeddings.shape}")
            return True
        else:
            print("❌ 模型路径不存在")
            return False
            
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("🔍 AI模型状态检查")
    print("=" * 50)
    
    # 检查文件状态
    files_ok = check_model_status()
    
    if files_ok:
        # 测试加载
        loading_ok = test_model_loading()
        
        if loading_ok:
            print("\n🎉 模型状态检查通过！")
            print("💡 可以正常启动系统了")
            print("\n启动命令:")
            print("  python run.py          # 完整启动")
            print("  python quick_start.py  # 快速启动")
        else:
            print("\n❌ 模型加载测试失败")
            print("💡 请尝试重新下载模型: python download_model.py")
    else:
        print("\n❌ 模型文件不完整")
        print("💡 请下载模型: python download_model.py")

if __name__ == "__main__":
    main() 