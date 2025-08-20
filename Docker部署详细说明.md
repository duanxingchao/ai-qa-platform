# 🐳 Docker化部署详细说明

## 📋 **Docker部署架构**

### **容器化服务组成**
```
智能问答系统 Docker 架构
├── qa-platform-backend     (后端API服务)
│   ├── Python 3.9 + Flask
│   ├── Gunicorn WSGI服务器
│   └── 端口: 8088
├── qa-platform-frontend    (前端Web服务)
│   ├── Vue.js 3 + Vite构建
│   ├── Nginx反向代理
│   └── 端口: 80, 443
├── qa-platform-redis       (缓存服务)
│   ├── Redis 6-alpine
│   └── 端口: 6379
└── qa-platform-prometheus  (监控服务)
    ├── Prometheus监控
    └── 端口: 9090
```

### **Docker网络配置**
```yaml
networks:
  qa-platform-network:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: qa-platform-br
      com.docker.network.driver.mtu: 1500
```

## 🌐 **代理环境下的Docker配置**

### **1. Docker Daemon代理配置**
```json
# /etc/docker/daemon.json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "proxies": {
    "default": {
      "httpProxy": "http://proxy-server:port",
      "httpsProxy": "http://proxy-server:port",
      "noProxy": "localhost,127.0.0.1,::1"
    }
  }
}
```

### **2. Docker服务代理配置**
```ini
# /etc/systemd/system/docker.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=http://proxy-server:port"
Environment="HTTPS_PROXY=http://proxy-server:port"
Environment="NO_PROXY=localhost,127.0.0.1,::1"
```

### **3. Docker Compose代理配置**
```yaml
# docker-compose.ubuntu18.yml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.ubuntu18
      args:
        - HTTP_PROXY=${HTTP_PROXY}
        - HTTPS_PROXY=${HTTPS_PROXY}
        - NO_PROXY=${NO_PROXY}
    environment:
      - HTTP_PROXY=${HTTP_PROXY}
      - HTTPS_PROXY=${HTTPS_PROXY}
      - NO_PROXY=${NO_PROXY}
```

## 🔧 **Dockerfile代理配置**

### **后端Dockerfile (backend/Dockerfile.ubuntu18)**
```dockerfile
# 代理参数
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# 设置代理环境变量（构建时使用）
ENV http_proxy=$HTTP_PROXY
ENV https_proxy=$HTTPS_PROXY
ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY
ENV NO_PROXY=$NO_PROXY

# 安装Python依赖时会使用代理
RUN pip install --no-cache-dir -r requirements.txt
```

### **前端Dockerfile (frontend/Dockerfile.ubuntu18)**
```dockerfile
# 代理参数
ARG HTTP_PROXY
ARG HTTPS_PROXY
ARG NO_PROXY

# 设置npm代理
RUN npm config set registry https://registry.npmmirror.com && \
    if [ -n "$HTTP_PROXY" ]; then npm config set proxy $HTTP_PROXY; fi && \
    if [ -n "$HTTPS_PROXY" ]; then npm config set https-proxy $HTTPS_PROXY; fi

# npm安装时会使用代理
RUN npm ci --only=production --silent
```

## 🚀 **Docker部署流程**

### **阶段1: 环境准备**
```bash
# 1. 配置系统代理
export http_proxy=http://proxy-server:port
export https_proxy=http://proxy-server:port

# 2. 配置Docker代理
sudo systemctl daemon-reload
sudo systemctl restart docker

# 3. 验证Docker代理
docker info | grep -i proxy
```

### **阶段2: 镜像构建**
```bash
# 1. 设置构建环境变量
export DOCKER_BUILDKIT=1
export BUILDKIT_PROGRESS=plain

# 2. 构建所有镜像
docker-compose -f docker-compose.ubuntu18.yml build

# 构建过程：
# - 下载基础镜像 (python:3.9-slim, node:16-alpine, nginx:1.20-alpine)
# - 安装系统依赖 (通过代理)
# - 安装Python包 (pip通过代理)
# - 安装npm包 (npm通过代理)
# - 构建前端资源
# - 配置Nginx
```

### **阶段3: 容器启动**
```bash
# 1. 启动所有服务
docker-compose -f docker-compose.ubuntu18.yml up -d

# 启动顺序：
# 1. redis (缓存服务)
# 2. backend (后端API，依赖redis)
# 3. frontend (前端服务，依赖backend)
# 4. prometheus (监控服务)

# 2. 检查容器状态
docker-compose -f docker-compose.ubuntu18.yml ps
```

### **阶段4: 服务验证**
```bash
# 1. 检查容器健康状态
docker-compose -f docker-compose.ubuntu18.yml exec backend curl -f http://localhost:8088/api/health
docker-compose -f docker-compose.ubuntu18.yml exec frontend curl -f http://localhost/health

# 2. 检查容器日志
docker-compose -f docker-compose.ubuntu18.yml logs backend
docker-compose -f docker-compose.ubuntu18.yml logs frontend

# 3. 检查网络连接
docker network ls
docker network inspect ai-qa-platform_qa-platform-network
```

## 📊 **容器资源配置**

### **内存限制**
```yaml
services:
  backend:
    mem_limit: 1g        # 后端服务1GB内存
    memswap_limit: 1g
  
  frontend:
    mem_limit: 512m      # 前端服务512MB内存
  
  redis:
    mem_limit: 512m      # Redis缓存512MB内存
  
  prometheus:
    mem_limit: 512m      # 监控服务512MB内存
```

### **端口映射**
```yaml
ports:
  - "80:80"      # 前端HTTP
  - "443:443"    # 前端HTTPS
  - "8088:8088"  # 后端API
  - "6379:6379"  # Redis缓存
  - "9090:9090"  # Prometheus监控
```

### **数据持久化**
```yaml
volumes:
  - ./logs:/app/logs           # 应用日志
  - ./uploads:/app/uploads     # 上传文件
  - redis_data:/data           # Redis数据
  - prometheus_data:/prometheus # 监控数据
```

## 🔍 **Docker部署验证**

### **容器状态检查**
```bash
# 检查所有容器状态
docker ps -a

# 检查特定服务状态
docker-compose -f docker-compose.ubuntu18.yml ps

# 检查容器资源使用
docker stats
```

### **网络连接测试**
```bash
# 测试容器间网络连接
docker-compose -f docker-compose.ubuntu18.yml exec backend ping redis
docker-compose -f docker-compose.ubuntu18.yml exec frontend ping backend

# 测试外部网络连接（通过代理）
docker-compose -f docker-compose.ubuntu18.yml exec backend curl -I https://www.google.com
```

### **服务功能测试**
```bash
# 测试后端API
curl http://localhost:8088/api/health
curl http://localhost:8088/api/dashboard

# 测试前端服务
curl http://localhost/health
curl -I http://localhost/

# 测试Redis连接
docker-compose -f docker-compose.ubuntu18.yml exec redis redis-cli ping
```

## 🚨 **Docker部署故障排除**

### **镜像构建失败**
```bash
# 检查代理配置
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 手动构建单个服务
docker-compose -f docker-compose.ubuntu18.yml build backend --no-cache

# 查看构建日志
docker-compose -f docker-compose.ubuntu18.yml build backend --progress=plain
```

### **容器启动失败**
```bash
# 查看容器日志
docker-compose -f docker-compose.ubuntu18.yml logs backend
docker-compose -f docker-compose.ubuntu18.yml logs frontend

# 进入容器调试
docker-compose -f docker-compose.ubuntu18.yml exec backend bash
docker-compose -f docker-compose.ubuntu18.yml exec frontend sh
```

### **网络连接问题**
```bash
# 检查Docker网络
docker network ls
docker network inspect ai-qa-platform_qa-platform-network

# 检查容器IP
docker inspect qa-platform-backend | grep IPAddress
docker inspect qa-platform-frontend | grep IPAddress
```

## ✅ **Docker部署成功标志**

当看到以下结果时，说明Docker部署成功：

1. ✅ 所有容器状态为 "Up" 和 "healthy"
2. ✅ 容器间网络连接正常
3. ✅ 后端API健康检查通过
4. ✅ 前端服务可访问
5. ✅ Redis缓存服务正常
6. ✅ 数据库连接成功
7. ✅ 外部API调用正常（如果配置）

**Docker化部署的优势：**
- 🔒 环境隔离和一致性
- 📦 简化部署和扩展
- 🔄 容易回滚和更新
- 📊 资源控制和监控
- 🌐 网络和代理配置统一管理
