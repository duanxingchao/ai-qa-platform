#!/bin/bash

# 智能问答系统代理环境快速部署脚本
# 整合所有部署步骤，支持内网代理环境

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

print_header() {
    echo
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================================${NC}"
    echo
}

# 检查是否为root用户
check_user() {
    if [[ $EUID -eq 0 ]]; then
        print_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 获取用户输入
get_user_input() {
    print_header "配置部署参数"
    
    # 代理配置
    echo -n "请输入代理服务器地址 (格式: http://proxy-server:port): "
    read PROXY_SERVER
    
    if [[ -z "$PROXY_SERVER" ]]; then
        print_error "代理服务器地址不能为空"
        exit 1
    fi
    
    echo -n "代理服务器是否需要用户名密码认证? (y/n): "
    read need_auth
    
    if [[ "$need_auth" == "y" ]] || [[ "$need_auth" == "Y" ]]; then
        echo -n "请输入用户名: "
        read proxy_username
        echo -n "请输入密码: "
        read -s proxy_password
        echo
        
        PROXY_SERVER=$(echo "$PROXY_SERVER" | sed "s|://|://${proxy_username}:${proxy_password}@|")
    fi
    
    # 数据库配置
    echo
    echo -n "请输入数据库主机地址: "
    read DB_HOST

    echo -n "请输入数据库密码: "
    read -s DB_PASSWORD
    echo

    if [[ -z "$DB_HOST" ]] || [[ -z "$DB_PASSWORD" ]]; then
        print_error "数据库主机地址和密码不能为空"
        exit 1
    fi

    # 构建数据库连接字符串
    DATABASE_URL="postgresql://dmp_rnd_xa:${DB_PASSWORD}@${DB_HOST}:8000/datalake"
    
    # API配置（可选）
    echo
    echo -n "是否配置外部API? (y/n): "
    read configure_api
    
    if [[ "$configure_api" == "y" ]] || [[ "$configure_api" == "Y" ]]; then
        echo -n "请输入分类API地址: "
        read CLASSIFICATION_API_URL
        echo -n "请输入分类API密钥: "
        read CLASSIFICATION_API_KEY
        echo -n "请输入AI生成API地址: "
        read AI_API_URL
        echo -n "请输入AI生成API密钥: "
        read AI_API_KEY
    fi
    
    print_message "配置收集完成！"
}

# 配置代理环境
setup_proxy() {
    print_header "配置代理环境"
    
    # 设置环境变量
    export http_proxy="$PROXY_SERVER"
    export https_proxy="$PROXY_SERVER"
    export HTTP_PROXY="$PROXY_SERVER"
    export HTTPS_PROXY="$PROXY_SERVER"
    export no_proxy="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
    export NO_PROXY="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
    
    # 添加到bashrc
    if ! grep -q "# Proxy Configuration" ~/.bashrc; then
        cat >> ~/.bashrc << EOF

# Proxy Configuration
export http_proxy="$PROXY_SERVER"
export https_proxy="$PROXY_SERVER"
export HTTP_PROXY="$PROXY_SERVER"
export HTTPS_PROXY="$PROXY_SERVER"
export no_proxy="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
export NO_PROXY="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
EOF
    fi
    
    # 配置APT代理
    sudo tee /etc/apt/apt.conf.d/95proxies > /dev/null << EOF
Acquire::http::Proxy "$PROXY_SERVER";
Acquire::https::Proxy "$PROXY_SERVER";
EOF
    
    # 配置Git代理
    git config --global http.proxy "$PROXY_SERVER"
    git config --global https.proxy "$PROXY_SERVER"
    
    print_message "✅ 代理环境配置完成"
}

# 测试代理连接
test_proxy() {
    print_step "测试代理连接..."
    
    if curl -s --connect-timeout 10 --proxy "$PROXY_SERVER" https://www.google.com > /dev/null; then
        print_message "✅ 代理连接测试成功"
    else
        print_error "❌ 代理连接测试失败，请检查代理配置"
        exit 1
    fi
}

# 运行系统兼容性检查
run_compatibility_check() {
    print_header "系统兼容性检查"
    
    if [[ -f "ubuntu18-compatibility-check.sh" ]]; then
        chmod +x ubuntu18-compatibility-check.sh
        ./ubuntu18-compatibility-check.sh
    else
        print_warning "兼容性检查脚本不存在，跳过检查"
    fi
}

# 安装Docker环境
install_docker_environment() {
    print_header "安装Docker环境"
    
    if [[ -f "deploy-ubuntu18.sh" ]]; then
        chmod +x deploy-ubuntu18.sh
        ./deploy-ubuntu18.sh
        
        # 重新加载用户组权限
        newgrp docker << EONG
        print_message "✅ Docker权限配置完成"
EONG
    else
        print_error "部署脚本不存在"
        exit 1
    fi
}

# 配置项目环境
configure_project() {
    print_header "配置项目环境"

    # 复制配置模板
    if [[ -f ".env.production" ]]; then
        cp .env.production .env
    else
        print_warning ".env.production 不存在，创建基础配置"
        touch .env
    fi

    # 生成安全密钥
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)

    # 写入配置
    cat > .env << EOF
# 数据库配置
DATABASE_URL=$DATABASE_URL
DATABASE_SCHEMA=dm_rnd_xa_export
SOURCE_TABLE_NAME=mid_pc_yoyo_qa_641000052

# 安全密钥
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY

# 代理配置（用于Docker构建和容器运行）
HTTP_PROXY=$PROXY_SERVER
HTTPS_PROXY=$PROXY_SERVER
NO_PROXY=localhost,127.0.0.1,::1,backend,frontend,redis,qa-platform-backend,qa-platform-frontend,qa-platform-redis

# Flask配置
FLASK_ENV=production
DEBUG=False
EOF

    # 添加API配置（如果有）
    if [[ -n "$CLASSIFICATION_API_URL" ]]; then
        cat >> .env << EOF

# 外部API配置
CLASSIFICATION_API_URL=$CLASSIFICATION_API_URL
CLASSIFICATION_API_KEY=$CLASSIFICATION_API_KEY
AI_API_URL=$AI_API_URL
AI_API_KEY=$AI_API_KEY
EOF
    fi

    print_message "✅ 项目环境配置完成"
    print_message "配置文件内容："
    echo "----------------------------------------"
    cat .env
    echo "----------------------------------------"
}

# 测试数据库连接
test_database() {
    print_header "测试数据库连接"
    
    if docker run --rm \
        --env http_proxy="$PROXY_SERVER" \
        --env https_proxy="$PROXY_SERVER" \
        postgres:13 \
        psql "$DATABASE_URL" \
        -c "SELECT version();" > /dev/null 2>&1; then
        print_message "✅ 数据库连接测试成功"
    else
        print_error "❌ 数据库连接测试失败，请检查数据库配置"
        exit 1
    fi
}

# 部署服务
deploy_services() {
    print_header "通过Docker部署服务"

    print_step "Docker部署流程说明："
    print_message "1. 🐳 构建Docker镜像（后端Python Flask + 前端Vue.js）"
    print_message "2. 🌐 配置容器网络和代理设置"
    print_message "3. 🚀 启动所有容器服务"
    print_message "4. 📊 启动监控和缓存服务"

    # 显示即将构建的服务
    print_step "即将构建的Docker服务："
    print_message "- qa-platform-backend (Python Flask API)"
    print_message "- qa-platform-frontend (Vue.js + Nginx)"
    print_message "- qa-platform-redis (Redis缓存)"
    print_message "- qa-platform-prometheus (监控服务)"

    # 检查Docker配置
    print_step "检查Docker代理配置..."
    if [[ -f "/etc/docker/daemon.json" ]]; then
        print_message "✅ Docker daemon代理配置已存在"
    else
        print_warning "⚠️ Docker daemon代理配置不存在"
    fi

    # 启动服务（Docker Compose）
    print_step "开始Docker构建和部署..."
    print_message "执行命令: docker-compose -f docker-compose.ubuntu18.yml up -d --build"

    # 设置构建时的代理环境变量
    export DOCKER_BUILDKIT=1
    export BUILDKIT_PROGRESS=plain

    if docker-compose -f docker-compose.ubuntu18.yml up -d --build; then
        print_message "✅ Docker服务构建和启动成功"
    else
        print_error "❌ Docker服务构建或启动失败"
        print_step "查看详细错误日志..."
        docker-compose -f docker-compose.ubuntu18.yml logs
        exit 1
    fi

    # 等待服务启动
    print_step "等待Docker容器完全启动..."
    sleep 30

    # 检查服务状态
    print_step "检查Docker容器状态..."
    docker-compose -f docker-compose.ubuntu18.yml ps

    if docker-compose -f docker-compose.ubuntu18.yml ps | grep -q "Up"; then
        print_message "✅ 所有Docker容器启动成功"
    else
        print_error "❌ 部分Docker容器启动失败"
        docker-compose -f docker-compose.ubuntu18.yml logs
        exit 1
    fi
}

# 初始化数据库
initialize_database() {
    print_header "初始化数据库"
    
    # 等待后端服务完全启动
    print_step "等待后端服务启动..."
    sleep 10
    
    # 创建数据库表
    docker-compose -f docker-compose.ubuntu18.yml exec -T backend python -c "
from app import create_app
from app.utils.database import db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ 数据库表创建完成')
" || print_warning "数据库初始化可能失败，请手动检查"
}

# 验证部署
verify_deployment() {
    print_header "验证部署"
    
    # 检查容器状态
    print_step "检查容器状态..."
    docker-compose -f docker-compose.ubuntu18.yml ps
    
    # 测试后端API
    print_step "测试后端API..."
    if curl -s http://localhost:18088/api/health | grep -q "healthy"; then
        print_message "✅ 后端API测试成功"
    else
        print_warning "⚠️ 后端API测试失败"
    fi
    
    # 测试前端服务
    print_step "测试前端服务..."
    if curl -s http://localhost:18080/health | grep -q "healthy"; then
        print_message "✅ 前端服务测试成功"
    else
        print_warning "⚠️ 前端服务测试失败"
    fi
    
    # 获取服务器IP
    SERVER_IP=$(hostname -I | awk '{print $1}')
    
    print_message "✅ 部署验证完成！"
    echo
    print_message "=== 访问信息 ==="
    print_message "前端页面: http://$SERVER_IP:18080"
    print_message "后端API: http://$SERVER_IP:18088"
    print_message "默认账号: admin"
    print_message "默认密码: admin123"
}

# 主函数
main() {
    print_header "智能问答系统代理环境快速部署"
    
    check_user
    get_user_input
    setup_proxy
    test_proxy
    run_compatibility_check
    install_docker_environment
    configure_project
    test_database
    deploy_services
    initialize_database
    verify_deployment
    
    print_header "部署完成！"
    print_message "🎉 智能问答系统已在代理环境下成功部署！"
}

# 错误处理
trap 'print_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"
