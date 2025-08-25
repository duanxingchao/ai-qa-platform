#!/bin/bash

# Docker代理环境构建脚本
# 专门解决在公司代理环境下Docker构建的各种网络问题：
# - apt-get update访问Debian官方源速度慢
# - apk update访问Alpine官方源速度慢
# - pip安装超时问题
# - npm安装超时问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 检查代理配置
check_proxy_config() {
    print_step "检查代理配置..."
    
    if [ -z "$HTTP_PROXY" ] && [ -z "$http_proxy" ]; then
        print_warning "未检测到HTTP代理配置"
        echo -n "是否需要设置代理? (y/n): "
        read need_proxy
        
        if [[ "$need_proxy" == "y" ]] || [[ "$need_proxy" == "Y" ]]; then
            echo -n "请输入代理服务器地址 (格式: http://proxy-server:port): "
            read proxy_server
            
            if [ -n "$proxy_server" ]; then
                export HTTP_PROXY="$proxy_server"
                export HTTPS_PROXY="$proxy_server"
                export http_proxy="$proxy_server"
                export https_proxy="$proxy_server"
                print_message "代理已设置: $proxy_server"
            fi
        fi
    else
        print_message "检测到代理配置:"
        [ -n "$HTTP_PROXY" ] && print_message "  HTTP_PROXY: $HTTP_PROXY"
        [ -n "$HTTPS_PROXY" ] && print_message "  HTTPS_PROXY: $HTTPS_PROXY"
    fi
    
    # 设置NO_PROXY
    export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16}"
    export no_proxy="$NO_PROXY"
}

# 配置Docker代理
configure_docker_proxy() {
    print_step "配置Docker代理..."
    
    if [ -n "$HTTP_PROXY" ]; then
        # 创建Docker daemon代理配置
        sudo mkdir -p /etc/systemd/system/docker.service.d
        
        sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf > /dev/null << EOF
[Service]
Environment="HTTP_PROXY=$HTTP_PROXY"
Environment="HTTPS_PROXY=$HTTPS_PROXY"
Environment="NO_PROXY=$NO_PROXY"
EOF
        
        # 创建Docker daemon.json配置
        if [ ! -f /etc/docker/daemon.json ]; then
            sudo tee /etc/docker/daemon.json > /dev/null << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
        fi
        
        # 重启Docker服务
        print_message "重启Docker服务以应用代理配置..."
        sudo systemctl daemon-reload
        sudo systemctl restart docker
        
        # 等待Docker服务启动
        sleep 5
        
        print_message "✅ Docker代理配置完成"
    else
        print_message "跳过Docker代理配置（未设置代理）"
    fi
}

# 测试Docker连接
test_docker_connectivity() {
    print_step "测试Docker连接..."
    
    # 测试Docker Hub连接
    if docker pull hello-world >/dev/null 2>&1; then
        print_message "✅ Docker Hub连接测试成功"
        docker rmi hello-world >/dev/null 2>&1 || true
    else
        print_warning "⚠️ Docker Hub连接测试失败，但继续构建..."
    fi
}

# 预拉取基础镜像
pull_base_images() {
    print_step "预拉取基础镜像..."
    
    local images=(
        "python:3.9-slim-bullseye"
        "redis:6-alpine"
        "nginx:alpine"
    )
    
    for image in "${images[@]}"; do
        print_message "拉取镜像: $image"
        if ! docker pull "$image"; then
            print_warning "拉取 $image 失败，构建时会自动重试"
        fi
    done
}

# 构建后端服务
build_backend() {
    print_step "构建后端服务..."
    
    cd backend
    
    # 确保优化脚本存在
    if [ ! -f "optimize-pip-install.sh" ]; then
        print_error "optimize-pip-install.sh 脚本不存在！"
        return 1
    fi
    
    # 构建参数
    local build_args=""
    [ -n "$HTTP_PROXY" ] && build_args="$build_args --build-arg HTTP_PROXY=$HTTP_PROXY"
    [ -n "$HTTPS_PROXY" ] && build_args="$build_args --build-arg HTTPS_PROXY=$HTTPS_PROXY"
    [ -n "$NO_PROXY" ] && build_args="$build_args --build-arg NO_PROXY=$NO_PROXY"
    
    print_message "构建参数: $build_args"
    
    # 执行构建
    if docker build $build_args -f Dockerfile.ubuntu18 -t qa-platform-backend:latest .; then
        print_message "✅ 后端服务构建成功"
    else
        print_error "❌ 后端服务构建失败"
        return 1
    fi
    
    cd ..
}

# 构建前端服务
build_frontend() {
    print_step "构建前端服务..."
    
    cd frontend
    
    # 构建参数
    local build_args=""
    [ -n "$HTTP_PROXY" ] && build_args="$build_args --build-arg HTTP_PROXY=$HTTP_PROXY"
    [ -n "$HTTPS_PROXY" ] && build_args="$build_args --build-arg HTTPS_PROXY=$HTTPS_PROXY"
    [ -n "$NO_PROXY" ] && build_args="$build_args --build-arg NO_PROXY=$NO_PROXY"
    
    # 执行构建
    if docker build $build_args -f Dockerfile.ubuntu18 -t qa-platform-frontend:latest .; then
        print_message "✅ 前端服务构建成功"
    else
        print_error "❌ 前端服务构建失败"
        return 1
    fi
    
    cd ..
}

# 使用docker-compose构建
build_with_compose() {
    print_step "使用docker-compose构建所有服务..."
    
    # 设置环境变量文件
    if [ ! -f ".env" ]; then
        print_warning ".env文件不存在，创建默认配置..."
        cp .env.production .env 2>/dev/null || {
            cat > .env << 'EOF'
# 代理配置
HTTP_PROXY=
HTTPS_PROXY=
NO_PROXY=localhost,127.0.0.1,::1

# 数据库配置
DATABASE_URL=postgresql://username:password@localhost:5432/dbname

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# API配置
CLASSIFICATION_API_URL=http://localhost:8001
AI_API_URL=http://localhost:8002
SCORING_API_URL=http://localhost:8003
CLASSIFICATION_API_KEY=test-key
AI_API_KEY=test-key
SCORING_API_KEY=test-key
EOF
        }
    fi
    
    # 更新.env文件中的代理配置
    if [ -n "$HTTP_PROXY" ]; then
        sed -i "s|^HTTP_PROXY=.*|HTTP_PROXY=$HTTP_PROXY|" .env
        sed -i "s|^HTTPS_PROXY=.*|HTTPS_PROXY=$HTTPS_PROXY|" .env
        sed -i "s|^NO_PROXY=.*|NO_PROXY=$NO_PROXY|" .env
    fi
    
    # 执行构建
    if docker-compose -f docker-compose.ubuntu18.yml build --no-cache; then
        print_message "✅ 所有服务构建成功"
    else
        print_error "❌ 服务构建失败"
        return 1
    fi
}

# 验证构建结果
verify_build() {
    print_step "验证构建结果..."
    
    local images=(
        "qa-platform-backend:latest"
        "qa-platform-frontend:latest"
    )
    
    for image in "${images[@]}"; do
        if docker images | grep -q "${image%:*}"; then
            print_message "✅ $image 构建成功"
        else
            print_error "❌ $image 构建失败"
            return 1
        fi
    done
    
    print_message "✅ 所有镜像构建验证通过"
}

# 显示使用说明
show_usage() {
    print_message "=== 构建完成！使用说明 ==="
    echo
    print_message "本次构建已优化以下问题："
    echo "  ✅ 替换Debian apt源为阿里云镜像源"
    echo "  ✅ 替换Alpine apk源为国内镜像源"
    echo "  ✅ 配置pip使用多个国内镜像源"
    echo "  ✅ 配置npm使用国内镜像源"
    echo "  ✅ 增加超时和重试机制"
    echo "  ✅ 支持公司代理环境"
    echo
    echo "1. 启动所有服务："
    echo "   docker-compose -f docker-compose.ubuntu18.yml up -d"
    echo
    echo "2. 查看服务状态："
    echo "   docker-compose -f docker-compose.ubuntu18.yml ps"
    echo
    echo "3. 查看服务日志："
    echo "   docker-compose -f docker-compose.ubuntu18.yml logs -f"
    echo
    echo "4. 停止所有服务："
    echo "   docker-compose -f docker-compose.ubuntu18.yml down"
    echo
    echo "5. 访问服务："
    echo "   前端: http://localhost:18080"
    echo "   后端: http://localhost:18088"
    echo
    print_message "如果仍有构建问题，请检查："
    echo "  - 代理服务器是否正常工作"
    echo "  - 网络连接是否稳定"
    echo "  - Docker daemon是否正确配置代理"
    echo
}

# 主函数
main() {
    print_message "Docker代理环境构建脚本 v1.0"
    print_message "================================"
    
    # 检查Docker是否安装
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    # 执行构建流程
    check_proxy_config
    configure_docker_proxy
    test_docker_connectivity
    pull_base_images
    
    # 选择构建方式
    echo
    echo "选择构建方式："
    echo "1. 使用docker-compose构建所有服务 (推荐)"
    echo "2. 分别构建后端和前端服务"
    echo -n "请选择 (1/2): "
    read build_choice
    
    case $build_choice in
        1)
            build_with_compose
            ;;
        2)
            build_backend
            build_frontend
            ;;
        *)
            print_message "使用默认方式：docker-compose构建"
            build_with_compose
            ;;
    esac
    
    verify_build
    show_usage
    
    print_message "✅ 构建流程完成！"
}

# 错误处理
trap 'print_error "构建过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
