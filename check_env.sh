#!/bin/bash

# KnowFlow 环境检查脚本
# 在启动服务前检查环境配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info "🔍 KnowFlow 环境检查工具"
echo "=" * 50

# 1. 检查 conda 环境
print_info "1. 检查 conda 环境..."
if command -v conda &> /dev/null; then
    print_success "Conda 已安装: $(conda --version)"
    
    # 检查 mineru 环境
    if conda info --envs | grep -q "mineru"; then
        print_success "mineru conda 环境存在"
    else
        print_error "mineru conda 环境不存在"
        echo "   请创建 mineru 环境: conda create -n mineru python=3.9"
    fi
else
    print_error "Conda 未安装"
fi

# 2. 检查 Python 依赖
print_info "2. 检查 Python 依赖..."
if command -v python &> /dev/null; then
    print_success "Python 已安装: $(python --version)"
    
    # 检查关键包
    packages=("fastapi" "uvicorn" "torch" "transformers")
    for pkg in "${packages[@]}"; do
        if python -c "import $pkg" &> /dev/null; then
            print_success "$pkg 已安装"
        else
            print_warning "$pkg 未安装"
        fi
    done
else
    print_error "Python 未安装"
fi

# 3. 检查 Node.js 和包管理器
print_info "3. 检查 Node.js 和包管理器..."
if command -v node &> /dev/null; then
    print_success "Node.js 已安装: $(node --version)"
    
    # 检查 npm
    if command -v npm &> /dev/null; then
        print_success "npm 已安装: $(npm --version)"
    else
        print_error "npm 未安装"
    fi
    
    # 检查 pnpm
    if command -v pnpm &> /dev/null; then
        print_success "pnpm 已安装: $(pnpm --version)"
    else
        print_warning "pnpm 未安装，建议安装: npm install -g pnpm"
    fi
else
    print_error "Node.js 未安装"
fi

# 4. 检查项目结构
print_info "4. 检查项目结构..."
required_dirs=("server" "web" "web_api")
for dir in "${required_dirs[@]}"; do
    if [ -d "$dir" ]; then
        print_success "$dir/ 目录存在"
    else
        print_error "$dir/ 目录不存在"
    fi
done

# 5. 检查配置文件
print_info "5. 检查配置文件..."
config_files=("web_api/app.py" "server/app.py" "web/package.json")
for file in "${config_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "$file 存在"
    else
        print_error "$file 不存在"
    fi
done

# 6. 检查端口占用
print_info "6. 检查端口占用..."
ports=(8888 5001 8081)
port_names=("MinerU" "后端" "前端")
for i in "${!ports[@]}"; do
    port=${ports[$i]}
    name=${port_names[$i]}
    if ss -tuln | grep -q ":$port "; then
        print_warning "$name 端口 $port 被占用"
    else
        print_success "$name 端口 $port 可用"
    fi
done

# 7. 检查 MinerU 特定环境
print_info "7. 检查 MinerU 特定环境..."
if [ -f "web_api/requirements.txt" ]; then
    print_success "web_api/requirements.txt 存在"
else
    print_warning "web_api/requirements.txt 不存在"
fi

# 8. 检查前端依赖
print_info "8. 检查前端依赖..."
if [ -d "web/node_modules" ]; then
    print_success "web/ 前端依赖已安装"
else
    print_warning "web/ 前端依赖未安装，需要运行: cd web && pnpm install"
fi

if [ -d "ragflow-ui/node_modules" ]; then
    print_success "ragflow-ui/ 前端依赖已安装"
else
    print_warning "ragflow-ui/ 前端依赖未安装，需要运行: cd ragflow-ui && npm install"
fi

# 总结
echo ""
echo "=" * 50
print_info "环境检查完成！"
print_info "如果有错误或警告，请先解决再启动服务。"
print_info "启动服务: ./start_knowflow.sh start"
print_info "查看帮助: ./start_knowflow.sh help" 