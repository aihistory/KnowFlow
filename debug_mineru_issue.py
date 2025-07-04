#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MinerU 服务诊断脚本
用于检查和修复 MinerU 服务问题
"""

import requests
import time
import subprocess
import json
import sys

def check_docker_status():
    """检查Docker是否运行"""
    print("🔍 检查 Docker 状态...")
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker 运行正常")
            return True
        else:
            print("❌ Docker 未运行")
            return False
    except FileNotFoundError:
        print("❌ Docker 未安装")
        return False

def check_mineru_container():
    """检查 MinerU 容器状态"""
    print("\n🔍 检查 MinerU 容器状态...")
    try:
        result = subprocess.run(['docker', 'ps', '-f', 'name=mineru-api'], 
                              capture_output=True, text=True)
        if 'mineru-api' in result.stdout:
            print("✅ MinerU 容器正在运行")
            
            # 获取容器详细信息
            inspect_result = subprocess.run(['docker', 'inspect', 'mineru-api'], 
                                          capture_output=True, text=True)
            if inspect_result.returncode == 0:
                container_info = json.loads(inspect_result.stdout)[0]
                print(f"   容器ID: {container_info['Id'][:12]}")
                print(f"   镜像: {container_info['Config']['Image']}")
                print(f"   状态: {container_info['State']['Status']}")
                print(f"   启动时间: {container_info['State']['StartedAt']}")
            return True
        else:
            print("❌ MinerU 容器未运行")
            return False
    except Exception as e:
        print(f"❌ 检查容器状态失败: {e}")
        return False

def check_mineru_api():
    """检查 MinerU API 健康状态"""
    print("\n🔍 检查 MinerU API 状态...")
    
    urls_to_check = [
        ("基础API", "http://localhost:8888/"),
        ("健康检查", "http://localhost:8888/health"),
        ("API文档", "http://localhost:8888/docs")
    ]
    
    all_ok = True
    for name, url in urls_to_check:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: {url} - 正常")
            else:
                print(f"⚠️  {name}: {url} - 状态码 {response.status_code}")
                all_ok = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: {url} - 连接失败")
            all_ok = False
        except requests.exceptions.Timeout:
            print(f"❌ {name}: {url} - 超时")
            all_ok = False
        except Exception as e:
            print(f"❌ {name}: {url} - 错误: {e}")
            all_ok = False
    
    return all_ok

def check_mineru_logs():
    """检查 MinerU 容器日志"""
    print("\n🔍 检查 MinerU 容器日志（最近20行）...")
    try:
        result = subprocess.run(['docker', 'logs', '--tail', '20', 'mineru-api'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 最近日志:")
            print("-" * 50)
            print(result.stdout)
            if result.stderr:
                print("⚠️  错误日志:")
                print(result.stderr)
            print("-" * 50)
        else:
            print("❌ 无法获取日志")
    except Exception as e:
        print(f"❌ 获取日志失败: {e}")

def restart_mineru_service(mode="auto"):
    """重启 MinerU 服务"""
    print(f"\n🔧 重启 MinerU 服务 (模式: {mode})...")
    
    # 停止现有容器
    print("停止现有容器...")
    subprocess.run(['docker', 'stop', 'mineru-api'], capture_output=True)
    subprocess.run(['docker', 'rm', 'mineru-api'], capture_output=True)
    
    # 根据模式选择启动命令
    if mode == "cpu":
        cmd = [
            'docker', 'run', '--rm', '-d',
            '--shm-size=16g',
            '-p', '8888:8888',
            '-e', 'MINERU_DEVICE_MODE=cpu',
            '--name', 'mineru-api',
            'zxwei/mineru-api:v1.0.0'
        ]
        print("使用 CPU 模式启动...")
    elif mode == "basic":
        cmd = [
            'docker', 'run', '--rm', '-d',
            '--shm-size=16g',
            '-p', '8888:8888',
            '--name', 'mineru-api',
            'zxwei/mineru-api:v1.0.0'
        ]
        print("使用基础镜像启动...")
    else:  # auto/gpu
        cmd = [
            'docker', 'run', '--rm', '-d', '--gpus=all',
            '--shm-size=32g',
            '-p', '8888:8888', '-p', '30000:30000',
            '--name', 'mineru-api',
            'zxwei/mineru-api-full:v1.0.0'
        ]
        print("使用 GPU 模式启动...")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 容器启动成功")
            print("⏳ 等待服务启动...")
            time.sleep(10)
            return True
        else:
            print(f"❌ 容器启动失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 启动容器时出错: {e}")
        return False

def test_document_processing():
    """测试文档处理功能"""
    print("\n🧪 测试文档处理功能...")
    
    # 这里可以添加一个简单的API测试
    try:
        # 检查 pipeline API 端点
        response = requests.get("http://localhost:8888/", timeout=10)
        if response.status_code == 200:
            print("✅ MinerU 服务响应正常")
            return True
        else:
            print(f"⚠️  MinerU 服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 测试文档处理失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 MinerU 服务诊断工具")
    print("=" * 50)
    
    # 检查命令行参数
    fix_mode = '--fix' in sys.argv
    cpu_mode = '--cpu' in sys.argv
    basic_mode = '--basic' in sys.argv
    
    # 1. 检查基础环境
    if not check_docker_status():
        print("\n💡 请先安装并启动 Docker")
        return
    
    # 2. 检查容器状态
    container_running = check_mineru_container()
    
    # 3. 检查 API 状态
    api_ok = False
    if container_running:
        api_ok = check_mineru_api()
        
        # 4. 查看日志
        if not api_ok:
            check_mineru_logs()
    
    # 5. 修复模式
    if fix_mode or not api_ok:
        if cpu_mode:
            mode = "cpu"
        elif basic_mode:
            mode = "basic"
        else:
            mode = "auto"
            
        if restart_mineru_service(mode):
            print("\n⏳ 重新检查服务状态...")
            time.sleep(5)
            if check_mineru_api():
                test_document_processing()
            else:
                print("❌ 服务重启后仍有问题，请检查日志")
    
    # 6. 提供建议
    print("\n" + "=" * 50)
    if api_ok:
        print("✅ MinerU 服务运行正常")
    else:
        print("💡 建议解决方案:")
        print("   1. 重启服务: python debug_mineru_issue.py --fix")
        print("   2. 使用CPU模式: python debug_mineru_issue.py --fix --cpu")
        print("   3. 使用基础镜像: python debug_mineru_issue.py --fix --basic")
        print("   4. 查看详细日志: docker logs -f mineru-api")

if __name__ == "__main__":
    main() 