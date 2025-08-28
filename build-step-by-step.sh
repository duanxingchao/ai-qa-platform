#!/bin/bash

# 分步骤Docker构建脚本 - 支持断点续传
# 解决构建时间长、中断后需要重新开始的问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 状态文件
STATE_FILE=".build-state"
STEP_STATUS_FILE=".step-status"

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
    echo -e "${BLUE}[STEP $1]${NC} $2"
}

print_substep() {
    echo -e "${CYAN}  → ${NC} $1"
}

# 记录步骤状态
mark_step_completed() {
    local step=$1
    echo "$step=completed" >> "$STEP_STATUS_FILE"
    print_message "✅ 步骤 $step 完成"
}

# 检查步骤是否已完成
is_step_completed() {
    local step=$1
    grep -q "^$step=completed$" "$STEP_STATUS_FILE" 2>/dev/null
}

# 显示进度
show_progress() {
    local completed=0
    local total=10
    
    if [ -f "$STEP_STATUS_FILE" ]; then
        completed=$(wc -l < "$STEP_STATUS_FILE")
    fi
    
    local percentage=$((completed * 100 / total))
    echo -e "${CYAN}📊 构建进度: ${completed}/${total} (${percentage}%)${NC}"
    
    # 显示进度条
    local bar_length=20
    local filled=$((completed * bar_length / total))
    local empty=$((bar_length - filled))
    
    printf "${CYAN}["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "]${NC}\n"
}

# 步骤1: 环境检查
step1_check_environment() {
    print_step "1" "环境检查与准备"
    
    if is_step_completed "step1"; then
        print_message "⏭️  步骤1已完成，跳过"
        return 0
    fi
    
    print_substep "检查Docker是否安装"
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    print_substep "检查Docker Compose是否安装"
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    print_substep "检查Docker服务状态"
    if ! systemctl is-active --quiet docker; then
        print_warning "Docker服务未运行，尝试启动..."
        sudo systemctl start docker
        sleep 5
    fi
    
    mark_step_completed "step1"
}

# 步骤2: 代理配置
step2_setup_proxy() {
    print_step "2" "配置网络代理"
    
    if is_step_completed "step2"; then
        print_message "⏭️  步骤2已完成，跳过"
        return 0
    fi
    
    print_substep "检查代理环境变量"
    if [ -z "$HTTP_PROXY" ] && [ -z "$HTTPS_PROXY" ]; then
        print_warning "未检测到代理配置"
        echo -n "请输入HTTP代理地址 (格式: http://proxy:port): "
        read proxy_url
        export HTTP_PROXY="$proxy_url"
        export HTTPS_PROXY="$proxy_url"
        export NO_PROXY="localhost,127.0.0.1,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12"
    fi
    
    print_substep "当前代理配置:"
    echo "  HTTP_PROXY: $HTTP_PROXY"
    echo "  HTTPS_PROXY: $HTTPS_PROXY"
    echo "  NO_PROXY: $NO_PROXY"
    
    mark_step_completed "step2"
}

# 步骤3: Docker代理配置
step3_configure_docker_proxy() {
    print_step "3" "配置Docker代理"
    
    if is_step_completed "step3"; then
        print_message "⏭️  步骤3已完成，跳过"
        return 0
    fi
    
    print_substep "配置Docker daemon代理"
    sudo mkdir -p /etc/systemd/system/docker.service.d
    
    cat << EOF | sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=$HTTP_PROXY"
Environment="HTTPS_PROXY=$HTTPS_PROXY"
Environment="NO_PROXY=$NO_PROXY"
EOF
    
    print_substep "重新加载systemd配置"
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    
    print_substep "等待Docker服务启动"
    sleep 10
    
    mark_step_completed "step3"
}

# 步骤4: 配置镜像源
step4_configure_registry() {
    print_step "4" "配置Docker镜像源"
    
    if is_step_completed "step4"; then
        print_message "⏭️  步骤4已完成，跳过"
        return 0
    fi
    
    print_substep "配置Docker daemon.json"
    cat << 'EOF' | sudo tee /etc/docker/daemon.json
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com"
    ]
}
EOF
    
    print_substep "重启Docker服务"
    sudo systemctl restart docker
    sleep 10
    
    mark_step_completed "step4"
}

# 步骤5: 清理旧容器和镜像
step5_cleanup() {
    print_step "5" "清理旧容器和镜像"
    
    if is_step_completed "step5"; then
        print_message "⏭️  步骤5已完成，跳过"
        return 0
    fi
    
    print_substep "停止并删除旧容器"
    docker-compose -f docker-compose.ubuntu18.yml down || true
    
    print_substep "删除悬空镜像"
    docker image prune -f || true
    
    mark_step_completed "step5"
}

# 步骤6: 下载基础镜像
step6_pull_base_images() {
    print_step "6" "下载基础镜像"
    
    if is_step_completed "step6"; then
        print_message "⏭️  步骤6已完成，跳过"
        return 0
    fi
    
    print_substep "下载Ubuntu 18.04基础镜像"
    timeout 1800 docker pull ubuntu:18.04 || {
        print_error "下载Ubuntu镜像超时，请检查网络连接"
        exit 1
    }
    
    print_substep "下载Node.js镜像"
    timeout 1800 docker pull node:16-alpine || {
        print_error "下载Node.js镜像超时，请检查网络连接"
        exit 1
    }
    
    print_substep "下载Python镜像"
    timeout 1800 docker pull python:3.8-slim || {
        print_error "下载Python镜像超时，请检查网络连接"
        exit 1
    }
    
    mark_step_completed "step6"
}

# 步骤7: 构建后端镜像
step7_build_backend() {
    print_step "7" "构建后端镜像"
    
    if is_step_completed "step7"; then
        print_message "⏭️  步骤7已完成，跳过"
        return 0
    fi
    
    print_substep "构建后端Docker镜像"
    cd backend
    timeout 1800 docker build \
        --build-arg HTTP_PROXY="$HTTP_PROXY" \
        --build-arg HTTPS_PROXY="$HTTPS_PROXY" \
        --build-arg NO_PROXY="$NO_PROXY" \
        -f Dockerfile.ubuntu18 \
        -t ai-qa-backend:latest . || {
        print_error "后端镜像构建超时或失败"
        cd ..
        exit 1
    }
    cd ..
    
    mark_step_completed "step7"
}

# 步骤8: 构建前端镜像
step8_build_frontend() {
    print_step "8" "构建前端镜像"
    
    if is_step_completed "step8"; then
        print_message "⏭️  步骤8已完成，跳过"
        return 0
    fi
    
    print_substep "构建前端Docker镜像"
    cd frontend
    timeout 1800 docker build \
        --build-arg HTTP_PROXY="$HTTP_PROXY" \
        --build-arg HTTPS_PROXY="$HTTPS_PROXY" \
        --build-arg NO_PROXY="$NO_PROXY" \
        -f Dockerfile.ubuntu18 \
        -t ai-qa-frontend:latest . || {
        print_error "前端镜像构建超时或失败"
        cd ..
        exit 1
    }
    cd ..
    
    mark_step_completed "step8"
}

# 步骤9: 验证镜像
step9_verify_images() {
    print_step "9" "验证构建的镜像"
    
    if is_step_completed "step9"; then
        print_message "⏭️  步骤9已完成，跳过"
        return 0
    fi
    
    print_substep "检查后端镜像"
    if ! docker images | grep -q "ai-qa-backend"; then
        print_error "后端镜像未找到"
        exit 1
    fi
    
    print_substep "检查前端镜像"
    if ! docker images | grep -q "ai-qa-frontend"; then
        print_error "前端镜像未找到"
        exit 1
    fi
    
    print_substep "显示构建的镜像信息"
    docker images | grep "ai-qa-"
    
    mark_step_completed "step9"
}

# 步骤10: 启动服务
step10_start_services() {
    print_step "10" "启动服务"
    
    if is_step_completed "step10"; then
        print_message "⏭️  步骤10已完成，跳过"
        return 0
    fi
    
    print_substep "启动Docker Compose服务"
    timeout 300 docker-compose -f docker-compose.ubuntu18.yml up -d || {
        print_error "服务启动超时或失败"
        exit 1
    }
    
    print_substep "等待服务启动完成"
    sleep 30
    
    print_substep "检查服务状态"
    docker-compose -f docker-compose.ubuntu18.yml ps
    
    mark_step_completed "step10"
}

# 主函数
main() {
    echo
    print_message "🚀 开始分步骤构建 AI-QA 平台"
    echo
    
    # 解析命令行参数
    case "${1:-}" in
        --status)
            show_progress
            if [ -f "$STEP_STATUS_FILE" ]; then
                echo
                print_message "已完成的步骤:"
                cat "$STEP_STATUS_FILE"
            fi
            exit 0
            ;;
        --reset)
            print_warning "重置构建状态"
            rm -f "$STEP_STATUS_FILE" "$STATE_FILE"
            print_message "状态已重置"
            exit 0
            ;;
        --step)
            if [ -z "$2" ]; then
                print_error "请指定步骤号 (1-10)"
                exit 1
            fi
            # 移除该步骤的完成状态
            grep -v "^step$2=completed$" "$STEP_STATUS_FILE" > "${STEP_STATUS_FILE}.tmp" 2>/dev/null || true
            mv "${STEP_STATUS_FILE}.tmp" "$STEP_STATUS_FILE" 2>/dev/null || true
            ;;
        --continue)
            print_message "从上次中断的地方继续构建"
            ;;
    esac
    
    show_progress
    echo
    
    # 执行构建步骤
    step1_check_environment
    step2_setup_proxy
    step3_configure_docker_proxy
    step4_configure_registry
    step5_cleanup
    step6_pull_base_images
    step7_build_backend
    step8_build_frontend
    step9_verify_images
    step10_start_services
    
    echo
    print_message "🎉 构建完成！"
    print_message "前端访问地址: http://localhost:3000"
    print_message "后端API地址: http://localhost:5000"
    echo
    print_message "使用以下命令管理服务:"
    echo "  查看状态: docker-compose -f docker-compose.ubuntu18.yml ps"
    echo "  查看日志: docker-compose -f docker-compose.ubuntu18.yml logs -f"
    echo "  停止服务: docker-compose -f docker-compose.ubuntu18.yml down"
}

# 脚本入口
main "$@"
