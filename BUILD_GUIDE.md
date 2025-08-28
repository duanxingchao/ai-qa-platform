# 🚀 分步骤构建指南

## 📋 问题解决

原有 `build-with-proxy.sh` 存在的问题：
- ❌ 构建时间长（30-60分钟）
- ❌ 中断后需要重新开始
- ❌ 重复下载相同内容
- ❌ 无法断点续传

## ✅ 新方案优势

使用 `build-step-by-step.sh` 的优势：
- ✅ **10个独立步骤**，每步可单独执行
- ✅ **断点续传**，中断后可继续
- ✅ **状态记录**，已完成步骤自动跳过
- ✅ **超时控制**，单步最长30分钟
- ✅ **分步验证**，每步验证后才继续

## 🔧 使用方法

### 1. 首次构建（推荐）
```bash
# 赋予执行权限
chmod +x build-step-by-step.sh

# 开始构建（自动执行所有步骤）
./build-step-by-step.sh
```

### 2. 查看当前状态
```bash
# 查看构建进度
./build-step-by-step.sh --status
```

### 3. 中断后继续
```bash
# 从上次中断的地方继续
./build-step-by-step.sh --continue
```

### 4. 重新构建特定步骤
```bash
# 重新构建后端（步骤7）
./build-step-by-step.sh --step 7

# 重新构建前端（步骤8）  
./build-step-by-step.sh --step 8
```

### 5. 完全重新开始
```bash
# 重置所有状态
./build-step-by-step.sh --reset

# 重新开始构建
./build-step-by-step.sh
```

## 📊 构建步骤详解

| 步骤 | 名称 | 时间预估 | 可跳过 | 说明 |
|------|------|----------|--------|------|
| 1 | 环境检查 | 30秒 | ✅ | 检查Docker、Docker Compose |
| 2 | 代理配置 | 1分钟 | ✅ | 配置HTTP/HTTPS代理 |
| 3 | Docker代理 | 2分钟 | ✅ | 配置Docker daemon代理 |
| 4 | 镜像源配置 | 1分钟 | ✅ | 配置国内镜像源 |
| 5 | 环境清理 | 2分钟 | ✅ | 清理旧容器和镜像 |
| 6 | 基础镜像下载 | 5-15分钟 | ❌ | 下载Ubuntu、Node、Python镜像 |
| 7 | 后端构建 | 10-20分钟 | ❌ | 构建后端Docker镜像 |
| 8 | 前端构建 | 10-20分钟 | ❌ | 构建前端Docker镜像 |
| 9 | 镜像验证 | 30秒 | ✅ | 验证构建的镜像 |
| 10 | 启动服务 | 2分钟 | ✅ | 启动Docker Compose服务 |

## 🎮 快速操作工具

### 使用 `quick-build.sh` 进行快速操作
```bash
# 赋予执行权限
chmod +x quick-build.sh

# 交互式菜单
./quick-build.sh

# 或直接执行特定操作
./quick-build.sh backend    # 重新构建后端
./quick-build.sh frontend   # 重新构建前端  
./quick-build.sh status     # 查看状态
./quick-build.sh start      # 启动服务
./quick-build.sh stop       # 停止服务
```

## 🚨 常见问题与解决方案

### 1. 构建中断问题
**现象**: 构建过程中网络中断或系统重启

**解决方案**:
```bash
# 查看当前进度
./build-step-by-step.sh --status

# 继续构建
./build-step-by-step.sh --continue
```

### 2. 网络代理问题
**现象**: 下载镜像失败，网络连接超时

**解决方案**:
```bash
# 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY

# 重新配置代理
export HTTP_PROXY="http://proxy.company.com:8080"
export HTTPS_PROXY="http://proxy.company.com:8080"

# 重新执行网络相关步骤
./build-step-by-step.sh --step 2
./build-step-by-step.sh --step 3
```

### 3. 磁盘空间不足
**现象**: 构建过程中提示磁盘空间不足

**解决方案**:
```bash
# 清理Docker缓存
docker system prune -f

# 删除无用镜像
docker image prune -f

# 查看磁盘使用情况
docker system df
```

### 4. 端口占用问题
**现象**: 服务启动失败，端口被占用

**解决方案**:
```bash
# 查看端口占用
netstat -tlnp | grep :3000
netstat -tlnp | grep :5000

# 停止占用端口的进程
sudo kill -9 <PID>

# 重新启动服务
./build-step-by-step.sh --step 10
```

### 5. 镜像构建失败
**现象**: 后端或前端镜像构建失败

**解决方案**:
```bash
# 查看详细错误日志
docker build --no-cache -f backend/Dockerfile.ubuntu18 backend/

# 重新构建特定组件
./build-step-by-step.sh --step 7  # 后端
./build-step-by-step.sh --step 8  # 前端
```

## 📁 文件说明

### 构建状态文件
- `.build-state`: 总体构建状态
- `.step-status`: 各步骤完成状态

### 重要配置文件
- `docker-compose.ubuntu18.yml`: Docker Compose配置
- `backend/Dockerfile.ubuntu18`: 后端镜像构建文件
- `frontend/Dockerfile.ubuntu18`: 前端镜像构建文件

## 🔍 调试技巧

### 1. 查看容器日志
```bash
# 查看所有服务日志
docker-compose -f docker-compose.ubuntu18.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.ubuntu18.yml logs -f backend
docker-compose -f docker-compose.ubuntu18.yml logs -f frontend
```

### 2. 进入容器调试
```bash
# 进入后端容器
docker-compose -f docker-compose.ubuntu18.yml exec backend bash

# 进入前端容器
docker-compose -f docker-compose.ubuntu18.yml exec frontend sh
```

### 3. 检查服务状态
```bash
# 查看容器状态
docker-compose -f docker-compose.ubuntu18.yml ps

# 查看系统资源使用
docker stats

# 查看镜像信息
docker images | grep ai-qa
```

## 🎯 最佳实践

### 1. 构建前准备
- 确保有足够的磁盘空间（至少10GB）
- 检查网络连接和代理设置
- 关闭不必要的应用程序

### 2. 构建过程中
- 不要中断正在下载的步骤
- 遇到错误及时查看日志
- 使用 `--status` 命令监控进度

### 3. 构建完成后
- 验证服务是否正常启动
- 测试前后端连通性
- 备份重要配置文件

## 📞 技术支持

如果遇到无法解决的问题，请提供以下信息：
1. 错误步骤和错误信息
2. 系统环境信息（操作系统、Docker版本）
3. 网络环境信息（是否使用代理）
4. 构建日志文件

---

💡 **提示**: 建议在非高峰时间进行构建，以获得更好的网络速度和系统性能。
