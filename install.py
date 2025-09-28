#!/usr/bin/env python3
"""
多语言智能客服系统安装脚本
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python版本过低: {version.major}.{version.minor}")
        print("需要Python 3.8或更高版本")
        return False
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def upgrade_pip():
    """升级pip"""
    return run_command("python -m pip install --upgrade pip", "升级pip")

def install_torch():
    """安装PyTorch"""
    print("🔥 安装PyTorch...")

    # 尝试不同的安装方式
    commands = [
        "pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu",
        "pip install torch torchvision",
        "conda install pytorch torchvision cpuonly -c pytorch"
    ]

    for i, command in enumerate(commands):
        print(f"尝试方式 {i+1}: {command}")
        if run_command(command, f"安装PyTorch (方式{i+1})"):
            return True

    print("❌ 所有PyTorch安装方式都失败了")
    return False

def install_other_dependencies():
    """安装其他依赖"""
    dependencies = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pillow",
        "opencv-python",
        "transformers",
        "sentence-transformers",
        "faiss-cpu",
        "pandas",
        "numpy",
        "requests",
        "python-dotenv",
        "jinja2",
        "aiofiles",
        "pydantic",
        "openai"
    ]

    print("📦 安装其他依赖...")
    for dep in dependencies:
        if not run_command(f"pip install {dep}", f"安装 {dep}"):
            print(f"⚠️ 警告: {dep} 安装失败，但继续安装其他依赖")

    return True

def create_env_file():
    """创建环境变量文件"""
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 创建.env文件...")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# AI千集API配置\n")
            f.write("AIQIANJI_API_KEY=your_AIQIANJI_API_KEY_here\n")
            f.write("AIQIANJI_BASE_URL=https://aiqianji.cn/v1\n\n")
            f.write("# 系统配置\n")
            f.write("DEBUG=True\n")
            f.write("LOG_LEVEL=INFO\n\n")
            f.write("# 服务器配置\n")
            f.write("HOST=0.0.0.0\n")
            f.write("PORT=8000\n")
        print("✅ .env文件创建成功")
        print("⚠️ 请编辑.env文件，添加您的AI千集API密钥")
    else:
        print("✅ .env文件已存在")

def test_installation():
    """测试安装"""
    print("🧪 测试安装...")

    test_imports = [
        ("fastapi", "FastAPI"),
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("sentence_transformers", "Sentence Transformers"),
        ("openai", "OpenAI"),
        ("faiss", "FAISS")
    ]

    failed_imports = []

    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} 导入成功")
        except ImportError as e:
            print(f"❌ {name} 导入失败: {e}")
            failed_imports.append(name)

    if failed_imports:
        print(f"\n⚠️ 以下模块导入失败: {', '.join(failed_imports)}")
        print("请手动安装这些模块")
        return False
    else:
        print("🎉 所有模块导入成功！")
        return True

def main():
    """主安装函数"""
    print("🚀 多语言智能客服系统安装程序")
    print("=" * 50)

    # 检查Python版本
    if not check_python_version():
        return False

    # 升级pip
    upgrade_pip()

    # 安装PyTorch
    if not install_torch():
        print("❌ PyTorch安装失败，请手动安装")
        print("建议访问: https://pytorch.org/get-started/locally/")
        return False

    # 安装其他依赖
    install_other_dependencies()

    # 创建环境文件
    create_env_file()

    # 测试安装
    if test_installation():
        print("\n🎉 安装完成！")
        print("\n📋 下一步:")
        print("1. 编辑.env文件，添加您的AI千集API密钥")
        print("2. 运行: python run.py")
        print("3. 访问: http://localhost:8000")
        return True
    else:
        print("\n⚠️ 安装完成，但部分模块可能有问题")
        print("请检查错误信息并手动安装失败的模块")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)