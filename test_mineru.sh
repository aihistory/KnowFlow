#!/bin/bash

# MinerU 服务测试启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info "🧪 测试 MinerU 服务启动"

# 检查当前目录
if [ ! -d "web_api" ]; then
    print_error "web_api 目录不存在"
    exit 1
fi

# 检查 conda 环境
print_info "检查 conda 环境..."
if ! conda info --envs | grep -q "mineru"; then
    print_error "mineru conda 环境不存在"
    exit 1
fi

# 设置环境变量
print_info "设置环境变量..."
export MINERU_DEVICE_MODE=cpu
export CUDA_VISIBLE_DEVICES=''

# 激活 conda 环境并启动服务
print_info "激活 mineru 环境并启动服务..."
echo "使用以下命令启动 MinerU："
echo "conda activate mineru"
echo "cd web_api"
echo "export MINERU_DEVICE_MODE=cpu"
echo "export CUDA_VISIBLE_DEVICES=''"
echo "python app.py"

# 实际启动
print_info "正在启动 MinerU 服务..."
cd web_api

# 使用 exec 让脚本在前台运行
exec bash -c "
    source ~/anaconda3/etc/profile.d/conda.sh
    conda activate mineru
    export MINERU_DEVICE_MODE=cpu
    export CUDA_VISIBLE_DEVICES=''
    python app.py
" 