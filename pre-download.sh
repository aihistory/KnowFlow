#!/bin/bash

# Docker 镜像预下载脚本
# 支持断点续传和多线程下载

echo "📥 开始预下载 Docker 镜像..."

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 镜像列表
IMAGES=(
    "zxwei/mineru-api:v1.0.0"
    "zxwei/mineru-api-full:v1.0.0"
    "zxwei/knowflow-web:v0.5.0"
    "zxwei/knowflow-server:v1.1.1"
    "gotenberg/gotenberg:8"
)

# 函数：下载单个镜像
download_image() {
    local image=$1
    echo -e "${YELLOW}📦 下载镜像: $image${NC}"
    
    # 使用 docker pull 并显示进度
    if docker pull "$image"; then
        echo -e "${GREEN}✅ 成功下载: $image${NC}"
        return 0
    else
        echo -e "${RED}❌ 下载失败: $image${NC}"
        return 1
    fi
}

# 函数：检查镜像是否已存在
check_image_exists() {
    local image=$1
    if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "^$image$"; then
        return 0
    else
        return 1
    fi
}

# 主下载逻辑
echo "🔍 检查现有镜像..."

for image in "${IMAGES[@]}"; do
    if check_image_exists "$image"; then
        echo -e "${GREEN}✅ 镜像已存在: $image${NC}"
    else
        echo -e "${YELLOW}⏳ 需要下载: $image${NC}"
        
        # 询问是否下载
        read -p "是否下载 $image? (y/n/a-全部下载): " choice
        case "$choice" in
            y|Y|yes|YES)
                download_image "$image"
                ;;
            a|A|all|ALL)
                echo "📥 下载所有缺失的镜像..."
                for img in "${IMAGES[@]}"; do
                    if ! check_image_exists "$img"; then
                        download_image "$img"
                    fi
                done
                break
                ;;
            *)
                echo "⏭️ 跳过: $image"
                ;;
        esac
    fi
done

# 显示镜像占用空间
echo ""
echo "💾 当前 Docker 镜像占用空间："
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep -E "(mineru|knowflow|gotenberg)"

echo ""
echo -e "${GREEN}🎉 预下载完成！${NC}"
echo "💡 提示：现在可以使用 docker-compose 启动服务了"