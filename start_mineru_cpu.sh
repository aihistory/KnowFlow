#!/bin/bash
# MinerU CPU 模式启动脚本

echo "🚀 启动 MinerU 服务 (CPU 模式)"
echo "================================"

# 激活 conda 环境
echo "📦 激活 conda 环境: mineru"
source $(conda info --base)/etc/profile.d/conda.sh
conda activate mineru

if [ "$CONDA_DEFAULT_ENV" != "mineru" ]; then
    echo "❌ 无法激活 mineru 环境，请检查 conda 配置"
    exit 1
fi

# 设置环境变量
echo "⚙️  设置环境变量 (CPU 模式)"
export MINERU_DEVICE_MODE=cpu
export CUDA_VISIBLE_DEVICES=""
export MINERU_MODEL_SOURCE=modelscope

echo "   MINERU_DEVICE_MODE=$MINERU_DEVICE_MODE"
echo "   CUDA_VISIBLE_DEVICES='$CUDA_VISIBLE_DEVICES'"
echo "   MINERU_MODEL_SOURCE=$MINERU_MODEL_SOURCE"

# 检查 web_api 目录
if [ ! -d "web_api" ]; then
    echo "❌ web_api 目录不存在，请在项目根目录运行此脚本"
    exit 1
fi

# 切换到 web_api 目录
cd web_api

# 检查必要文件
if [ ! -f "app.py" ]; then
    echo "❌ app.py 文件不存在"
    exit 1
fi

echo "🔥 启动 MinerU 服务..."
echo "   服务地址: http://localhost:8888"
echo "   API 文档: http://localhost:8888/docs"
echo "   停止服务: Ctrl+C"
echo ""

# 启动服务
python app.py 