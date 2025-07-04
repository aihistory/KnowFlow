# 🚀 Docker 镜像下载加速指南

Docker 镜像下载慢的问题可以通过多种方法解决，本指南提供了完整的解决方案。

## 📊 镜像大小对比

| 镜像 | 大小 | 功能 | 推荐场景 |
|------|------|------|----------|
| `zxwei/mineru-api:v1.0.0` | ~2-3GB | 基础功能 | 快速测试 |
| `zxwei/mineru-api-full:v1.0.0` | ~5-10GB | 完整功能 | 生产环境 |

## 🛠️ 解决方案（按优先级排序）

### 方案一：配置镜像加速器（必做）

```bash
# 1. 运行自动配置脚本
chmod +x docker-acceleration.sh
sudo ./docker-acceleration.sh

# 2. 验证配置
docker info | grep -A 10 "Registry Mirrors"
```

**手动配置（如果脚本失败）：**
```bash
# 编辑 Docker 配置
sudo nano /etc/docker/daemon.json

# 添加以下内容
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://reg-mirror.qiniu.com"
  ],
  "max-concurrent-downloads": 10
}

# 重启 Docker
sudo systemctl restart docker
```

### 方案二：使用快速版本镜像（推荐）

```bash
# 使用基础版镜像，下载速度快 3-5 倍
docker-compose -f docker-compose.fast.yml up -d
```

### 方案三：预下载脚本

```bash
# 1. 给脚本执行权限
chmod +x pre-download.sh

# 2. 运行预下载
./pre-download.sh

# 3. 选择性下载需要的镜像
```

### 方案四：分层下载策略

```bash
# 1. 先下载基础镜像
docker pull python:3.11-slim
docker pull nvidia/cuda:11.8-base-ubuntu20.04

# 2. 再下载应用镜像
docker pull zxwei/mineru-api:v1.0.0
```

### 方案五：并行下载优化

在 `daemon.json` 中增加并行下载配置：
```json
{
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5,
  "max-download-attempts": 5
}
```

## 🌐 网络优化方案

### 1. 使用代理加速
```bash
# 临时设置代理
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port

# 重启 Docker 服务
sudo systemctl restart docker
```

### 2. DNS 优化
```bash
# 添加公共 DNS
sudo nano /etc/resolv.conf

# 添加以下内容
nameserver 8.8.8.8
nameserver 114.114.114.114
```

### 3. 时间窗口优化
**最佳下载时间：**
- 🌅 早上 6:00-9:00
- 🌃 晚上 23:00-凌晨 2:00
- 📊 避开网络高峰期

## 📈 效果测试

### 下载速度对比
```bash
# 测试下载速度
time docker pull zxwei/mineru-api:v1.0.0

# 查看下载进度
docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
```

### 预期提升效果
- **配置加速器**: 提升 2-5 倍
- **使用基础镜像**: 减少 60-70% 下载量
- **并行下载**: 提升 1.5-2 倍
- **综合优化**: 总体提升 5-10 倍

## 🔧 故障排除

### 问题1：加速器配置失败
```bash
# 检查配置文件
sudo cat /etc/docker/daemon.json

# 验证语法
sudo dockerd --validate

# 查看 Docker 服务状态
sudo systemctl status docker
```

### 问题2：仍然下载很慢
```bash
# 1. 清理 Docker 缓存
docker system prune -a

# 2. 尝试不同的镜像源
sudo nano /etc/docker/daemon.json
# 更换 registry-mirrors 顺序

# 3. 使用基础版镜像
docker-compose -f docker-compose.fast.yml up -d
```

### 问题3：磁盘空间不足
```bash
# 清理无用镜像
docker image prune -a

# 查看磁盘使用情况
docker system df

# 清理所有无用数据
docker system prune -a --volumes
```

## 📋 快速操作清单

### ✅ 立即可做的优化
- [ ] 运行 `docker-acceleration.sh` 配置加速器
- [ ] 使用 `docker-compose.fast.yml` 启动基础版本
- [ ] 设置并行下载参数

### ⏰ 中期优化
- [ ] 配置网络代理（如有条件）
- [ ] 优化下载时间窗口
- [ ] 预下载常用镜像

### 🔄 长期维护
- [ ] 定期清理无用镜像
- [ ] 监控镜像更新
- [ ] 优化存储配置

## 🎯 推荐快速方案

**新手用户（最简单）：**
```bash
# 1. 配置加速器
sudo ./docker-acceleration.sh

# 2. 使用快速版本
docker-compose -f docker-compose.fast.yml up -d
```

**高级用户（最优化）：**
```bash
# 1. 完整配置加速器
sudo ./docker-acceleration.sh

# 2. 预下载镜像
./pre-download.sh

# 3. 启动完整服务
docker-compose -f docker-compose.integrated.yml up -d
```

## 📞 获取帮助

如果以上方案都无法解决问题：
1. 检查网络连接状态
2. 尝试使用移动热点
3. 考虑使用 VPN 服务
4. 联系网络服务提供商

---

**最后更新：** 2025-01-14  
**测试环境：** Ubuntu 20.04+, Docker 24.0+