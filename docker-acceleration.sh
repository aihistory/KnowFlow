#!/bin/bash

# Docker 镜像加速配置脚本
# 适用于 Linux 系统

echo "🚀 配置 Docker 镜像加速器..."

# 1. 备份原有配置
if [ -f /etc/docker/daemon.json ]; then
    sudo cp /etc/docker/daemon.json /etc/docker/daemon.json.backup
    echo "✅ 已备份原有配置"
fi

# 2. 创建或更新 Docker 配置
sudo mkdir -p /etc/docker

# 3. 配置多个镜像源
cat << EOF | sudo tee /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://reg-mirror.qiniu.com",
    "https://registry.docker-cn.com",
    "h5oaaa48.mirror.aliyuncs.com"
  ],
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
EOF

echo "✅ 配置文件已更新"

# 4. 重启 Docker 服务
echo "🔄 重启 Docker 服务..."
sudo systemctl daemon-reload
sudo systemctl restart docker

# 5. 验证配置
echo "🔍 验证配置..."
docker info | grep -A 5 "Registry Mirrors"

echo "🎉 Docker 加速器配置完成！"
echo "💡 提示：如果仍然很慢，可以尝试使用基础版镜像或手动下载"