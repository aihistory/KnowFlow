#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MinerU 本地开发环境诊断脚本
用于检查和修复本地 MinerU 服务问题
"""

import os
import sys
import subprocess
import requests
import time
import json
from pathlib import Path

def check_conda_env():
    """检查conda环境"""
    print("🔍 检查 conda 环境...")
    
    # 检查当前是否在conda环境中
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print(f"✅ 当前 conda 环境: {conda_env}")
        
        # 检查是否是 mineru 环境
        if conda_env == 'mineru':
            print("✅ 正在使用 mineru 环境")
        else:
            print("⚠️  当前不是 mineru 环境")
            return False
    else:
        print("❌ 未检测到 conda 环境")
        return False
    
    return True

def check_python_packages():
    """检查Python包依赖"""
    print("\n🔍 检查关键 Python 包...")
    
    # 基础包
    basic_packages = [
        'torch',
        'transformers',
        'fastapi',
        'uvicorn',
        'mineru'
    ]
    
    # MinerU 特定依赖包
    mineru_packages = [
        'doclayout_yolo',
        'torchvision',
        'ultralytics',
        'opencv-python'
    ]
    
    all_packages = basic_packages + mineru_packages
    missing_packages = []
    
    for package in all_packages:
        try:
            # 特殊处理一些包名
            import_name = package
            if package == 'opencv-python':
                import_name = 'cv2'
            elif package == 'doclayout_yolo':
                import_name = 'doclayout_yolo'
            
            result = subprocess.run([sys.executable, '-c', f'import {import_name}; print("OK")'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package}: 已安装")
            else:
                print(f"❌ {package}: 未安装或导入失败")
                missing_packages.append(package)
        except Exception as e:
            print(f"❌ {package}: 检查失败 - {e}")
            missing_packages.append(package)
    
    return missing_packages

def check_pytorch_device():
    """检查PyTorch设备配置"""
    print("\n🔍 检查 PyTorch 设备配置...")
    
    try:
        result = subprocess.run([sys.executable, '-c', 
                                'import torch; print("CUDA available:", torch.cuda.is_available()); print("Device count:", torch.cuda.device_count()); print("Current device:", torch.cuda.current_device() if torch.cuda.is_available() else "CPU")'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 PyTorch 设备信息:")
            print(result.stdout)
        else:
            print("❌ PyTorch 设备检查失败")
    except Exception as e:
        print(f"❌ PyTorch 设备检查出错: {e}")

def check_mineru_service():
    """检查MinerU服务状态"""
    print("\n🔍 检查 MinerU 服务状态...")
    
    urls_to_check = [
        ("基础API", "http://localhost:8888/"),
        ("健康检查", "http://localhost:8888/health"),
        ("API文档", "http://localhost:8888/docs")
    ]
    
    service_running = False
    for name, url in urls_to_check:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: 正常")
                service_running = True
            else:
                print(f"⚠️  {name}: 状态码 {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: 连接失败")
        except requests.exceptions.Timeout:
            print(f"❌ {name}: 超时")
        except Exception as e:
            print(f"❌ {name}: 错误: {e}")
    
    return service_running

def check_web_api_directory():
    """检查web_api目录结构"""
    print("\n🔍 检查 web_api 目录...")
    
    current_dir = Path.cwd()
    web_api_dir = current_dir / "web_api"
    
    if web_api_dir.exists():
        print(f"✅ web_api 目录存在: {web_api_dir}")
        
        # 检查关键文件
        key_files = ["app.py", "requirements.txt", "mineru.json"]
        for file in key_files:
            file_path = web_api_dir / file
            if file_path.exists():
                print(f"✅ {file}: 存在")
            else:
                print(f"❌ {file}: 不存在")
    else:
        print(f"❌ web_api 目录不存在: {web_api_dir}")
        return False
    
    return True

def install_missing_packages(missing_packages):
    """安装缺失的包"""
    if not missing_packages:
        return True
    
    print(f"\n🔧 安装缺失的包: {', '.join(missing_packages)}")
    
    # 重要：按照正确的顺序安装
    install_commands = []
    
    # 检查是否缺少核心 MinerU 包
    if 'doclayout_yolo' in missing_packages:
        print("💡 检测到缺少 doclayout_yolo，将重新安装完整的 MinerU")
        install_commands = [
            'pip install --upgrade pip',
            'pip install "mineru[core]"',  # 安装核心版本，这会自动安装 doclayout_yolo
        ]
        # 检查其他缺失的包
        for package in missing_packages:
            if package not in ['mineru', 'doclayout_yolo']:
                install_commands.append(f'pip install {package}')
    else:
        # 只安装缺失的基础包
        for package in missing_packages:
            if package not in ['mineru']:  # mineru 需要特殊处理
                install_commands.append(f'pip install {package}')
    
    print("🔧 执行安装命令:")
    for cmd in install_commands:
        print(f"   {cmd}")
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ 成功")
            else:
                print(f"   ❌ 失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ 执行失败: {e}")
            return False
    
    return True

def fix_pytorch_device_issue():
    """修复PyTorch设备问题"""
    print("\n🔧 尝试修复 PyTorch 设备问题...")
    
    # 设置环境变量强制使用CPU
    os.environ['MINERU_DEVICE_MODE'] = 'cpu'
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    
    print("✅ 设置环境变量:")
    print("   MINERU_DEVICE_MODE=cpu")
    print("   CUDA_VISIBLE_DEVICES=''")
    
    # 清理PyTorch缓存
    try:
        result = subprocess.run([sys.executable, '-c', 
                                'import torch; torch.cuda.empty_cache(); print("PyTorch缓存已清理")'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ PyTorch 缓存已清理")
        else:
            print("⚠️  PyTorch 缓存清理失败")
    except Exception as e:
        print(f"⚠️  PyTorch 缓存清理出错: {e}")

def create_mineru_config():
    """创建MinerU配置文件"""
    print("\n🔧 创建/更新 MinerU 配置...")
    
    config_path = Path("web_api/mineru.json")
    
    # 安全的配置，强制使用CPU
    safe_config = {
        "bucket_info": {},
        "latex-delimiter-config": {
            "display": {"left": "$$", "right": "$$"},
            "inline": {"left": "$", "right": "$"}
        },
        "llm-aided-config": {
            "title_aided": {
                "api_key": "your_api_key",
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model": "qwen2.5-32b-instruct",
                "enable": False
            }
        },
        "models-dir": {
            "pipeline": "",
            "vlm": ""
        },
        "device-mode": "cpu",  # 强制CPU模式
        "config_version": "1.3.0"
    }
    
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(safe_config, f, indent=2, ensure_ascii=False)
        print(f"✅ 配置文件已创建: {config_path}")
    except Exception as e:
        print(f"❌ 创建配置文件失败: {e}")

def restart_mineru_service():
    """重启MinerU服务"""
    print("\n🔧 重启 MinerU 服务...")
    
    # 检查web_api目录
    if not Path("web_api").exists():
        print("❌ web_api 目录不存在，请确认当前目录正确")
        return False
    
    print("💡 请手动重启 MinerU 服务:")
    print("   1. 停止当前服务 (Ctrl+C)")
    print("   2. 激活conda环境: conda activate mineru")
    print("   3. 进入目录: cd web_api")
    print("   4. 设置环境变量: export MINERU_DEVICE_MODE=cpu")
    print("   5. 启动服务: python app.py")
    
    return True

def main():
    """主函数"""
    print("🔧 MinerU 本地开发环境诊断工具")
    print("=" * 50)
    
    # 检查命令行参数
    fix_mode = '--fix' in sys.argv
    install_mode = '--install' in sys.argv
    
    # 1. 检查conda环境
    if not check_conda_env():
        print("\n💡 请激活 mineru conda 环境:")
        print("   conda activate mineru")
        return
    
    # 2. 检查Python包
    missing_packages = check_python_packages()
    if missing_packages:
        print(f"\n💡 缺少以下包: {', '.join(missing_packages)}")
        
        if install_mode or fix_mode:
            print("🔧 开始安装缺失的包...")
            if install_missing_packages(missing_packages):
                print("✅ 包安装完成，请重新运行诊断")
                print("   python debug_mineru_local.py")
            else:
                print("❌ 包安装失败，请手动安装:")
                print("   pip install \"mineru[core]\"")
                print("   pip install doclayout_yolo  # 如果上面的命令没有自动安装这个包")
            return
        else:
            print("   运行安装: python debug_mineru_local.py --install")
            return
    
    # 3. 检查PyTorch设备
    check_pytorch_device()
    
    # 4. 检查web_api目录
    if not check_web_api_directory():
        print("\n💡 请确认当前目录包含 web_api 子目录")
        return
    
    # 5. 检查服务状态
    service_ok = check_mineru_service()
    
    # 6. 修复模式
    if fix_mode and not service_ok:
        fix_pytorch_device_issue()
        create_mineru_config()
        restart_mineru_service()
    
    # 7. 提供建议
    print("\n" + "=" * 50)
    if service_ok:
        print("✅ MinerU 服务运行正常")
    elif missing_packages:
        print("💡 建议解决方案:")
        print("   1. 安装缺失包: python debug_mineru_local.py --install")
        print("   2. 手动安装: pip install \"mineru[core]\" doclayout_yolo")
    else:
        print("💡 建议解决方案:")
        print("   1. 运行修复: python debug_mineru_local.py --fix")
        print("   2. 手动重启服务（使用CPU模式）")
        print("   3. 检查依赖包是否完整")
        print("   4. 确认 conda 环境正确")

if __name__ == "__main__":
    main() 