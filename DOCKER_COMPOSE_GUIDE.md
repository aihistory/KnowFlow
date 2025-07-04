# Docker Compose 配置文件使用指南

本项目提供了多个 Docker Compose 配置文件，用于不同的部署场景：

## 配置文件说明

### 1. `docker-compose.mineru-simple.yml` - 最简配置（推荐新手）
```yaml
# 最简单的 MinerU 服务配置
# 功能：完整版 MinerU 服务，包含所有功能
# 适用：快速测试和开发环境
```

**启动方式：**
```bash
docker-compose -f docker-compose.mineru-simple.yml up -d
```

### 2. `docker-compose.mineru-basic.yml` - 基础版本
```yaml
# 使用基础版 MinerU 镜像
# 功能：仅包含核心文档解析功能
# 适用：对功能要求不高，需要快速部署的场景
```

**启动方式：**
```bash
docker-compose -f docker-compose.mineru-basic.yml up -d
```

### 3. `docker-compose.mineru.yml` - 完整独立版
```yaml
# 完整的 MinerU 服务配置
# 功能：包含数据持久化、健康检查、网络配置等
# 适用：生产环境单独部署 MinerU 服务
```

**启动方式：**
```bash
docker-compose -f docker-compose.mineru.yml up -d
```

### 4. `docker-compose.integrated.yml` - 集成版本（推荐）
```yaml
# 集成 MinerU + KnowFlow 完整解决方案
# 功能：一键部署所有服务（MinerU、KnowFlow前端、后端、Gotenberg）
# 适用：生产环境完整部署
```

**启动方式：**
```bash
# 1. 确保 .env 文件已配置
cp .env.example .env
# 编辑 .env 文件，填写必要配置

# 2. 启动所有服务
docker-compose -f docker-compose.integrated.yml up -d
```

## 选择建议

### 🆕 **新手用户**
推荐使用：`docker-compose.mineru-simple.yml`
- 配置简单，快速上手
- 包含完整功能

### 🏢 **生产环境**
推荐使用：`docker-compose.integrated.yml`
- 一键部署完整解决方案
- 包含所有必要服务
- 支持数据持久化

### 🔧 **开发调试**
推荐使用：`docker-compose.mineru.yml`
- 完整的配置选项
- 独立部署，方便调试
- 包含健康检查

### 💾 **资源受限**
推荐使用：`docker-compose.mineru-basic.yml`
- 使用基础版镜像，体积更小
- 资源消耗较低
- 核心功能完整

## 常用操作

### 启动服务
```bash
# 后台启动
docker-compose -f [配置文件] up -d

# 查看日志
docker-compose -f [配置文件] logs -f

# 查看服务状态
docker-compose -f [配置文件] ps
```

### 停止服务
```bash
# 停止服务
docker-compose -f [配置文件] down

# 停止并删除数据卷
docker-compose -f [配置文件] down -v
```

### 更新镜像
```bash
# 拉取最新镜像
docker-compose -f [配置文件] pull

# 重新构建并启动
docker-compose -f [配置文件] up -d --build
```

## 网络配置

### 服务间通信
- MinerU 服务：`http://mineru-api:8888`
- KnowFlow 后端：`http://backend:5000`
- Gotenberg 服务：`http://gotenberg:3000`

### 外部访问
- MinerU API：`http://localhost:8888`
- KnowFlow 前端：`http://localhost:8081`
- KnowFlow 后端：`http://localhost:5000`

## 故障排除

### 1. GPU 不可用
```bash
# 检查 GPU 支持
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# 安装 nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. 端口冲突
```bash
# 查看端口占用
sudo netstat -tulpn | grep :8888
sudo lsof -i :8888

# 修改配置文件中的端口映射
```

### 3. 内存不足
```bash
# 增加 Docker 内存限制
# 或者调整 shm_size 参数
```

### 4. 网络连接问题
```bash
# 检查容器网络
docker network ls
docker network inspect [network_name]

# 测试服务连通性
docker exec -it [container_name] curl http://mineru-api:8888/health
```

## 环境变量配置

### 必需环境变量
```env
RAGFLOW_API_KEY=your_api_key_here
RAGFLOW_BASE_URL=http://your_ragflow_host:port
```

### 可选环境变量
```env
DB_HOST=your_database_host
MINIO_HOST=your_minio_host
ES_HOST=your_elasticsearch_host
ES_PORT=9200
MANAGEMENT_ADMIN_USERNAME=admin
MANAGEMENT_ADMIN_PASSWORD=secure_password
MANAGEMENT_JWT_SECRET=your_jwt_secret
```

## 数据持久化

### 数据卷说明
- `mineru_data`：MinerU 应用数据
- `mineru_models`：MinerU 模型文件

### 备份数据
```bash
# 备份数据卷
docker run --rm -v mineru_data:/data -v $(pwd):/backup alpine tar czf /backup/mineru_data.tar.gz /data

# 恢复数据卷
docker run --rm -v mineru_data:/data -v $(pwd):/backup alpine tar xzf /backup/mineru_data.tar.gz -C /
```

## 性能优化

### 1. 资源限制
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      cpus: '2'
      memory: 4G
```

### 2. 并发配置
```yaml
environment:
  - WORKERS=4
  - MAX_REQUESTS=1000
```

### 3. 缓存优化
```yaml
volumes:
  - ./cache:/app/cache
```

---

**更新日期：** 2025-01-14
**适用版本：** KnowFlow v0.5.0+