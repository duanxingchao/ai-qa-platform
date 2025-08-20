#!/bin/bash

# 智能问答系统Ubuntu 18.04优化部署脚本
# 专门针对Ubuntu 18.04进行鲁棒性优化

set -e  # 遇到错误立即退出

echo "🚀 开始部署智能问答系统到Ubuntu 18.04生产环境..."

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

# 检查系统版本
check_system() {
    print_step "检查系统环境..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        print_message "操作系统: $NAME $VERSION"
        
        if [[ "$NAME" == "Ubuntu" ]]; then
            if [[ "$VERSION_ID" == "18.04" ]]; then
                print_message "✅ Ubuntu 18.04 检测通过，使用优化配置"
                UBUNTU_18=true
            elif [[ "$VERSION_ID" == "20.04" ]] || [[ "$VERSION_ID" == "22.04" ]]; then
                print_message "✅ Ubuntu $VERSION_ID 检测通过"
                UBUNTU_18=false
            else
                print_warning "未测试的Ubuntu版本: $VERSION_ID"
                UBUNTU_18=false
            fi
        else
            print_warning "非Ubuntu系统，可能需要手动调整"
            UBUNTU_18=false
        fi
    else
        print_error "无法检测系统版本"
        exit 1
    fi
}

# 检查网络连接
check_network() {
    print_step "检查网络连接..."
    
    # 检查DNS解析
    if nslookup google.com > /dev/null 2>&1; then
        print_message "✅ DNS解析正常"
    else
        print_error "❌ DNS解析失败，请检查网络配置"
        exit 1
    fi
    
    # 检查外网连接
    if curl -s --connect-timeout 5 https://www.google.com > /dev/null; then
        print_message "✅ 外网连接正常"
    else
        print_warning "⚠️ 外网连接异常，可能影响Docker镜像下载"
    fi
    
    # 检查Docker Hub连接
    if curl -s --connect-timeout 5 https://hub.docker.com > /dev/null; then
        print_message "✅ Docker Hub连接正常"
    else
        print_warning "⚠️ Docker Hub连接异常，将使用国内镜像源"
        USE_MIRROR=true
    fi
}

# 更新系统包
update_system() {
    print_step "更新系统包..."
    
    # 更新包列表
    sudo apt-get update
    
    # 安装基础依赖
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release \
        software-properties-common \
        wget \
        unzip
    
    print_message "✅ 系统包更新完成"
}

# 安装Docker (Ubuntu 18.04优化)
install_docker() {
    print_step "安装Docker..."
    
    if command -v docker &> /dev/null; then
        print_message "Docker已安装: $(docker --version)"
        return 0
    fi
    
    # Ubuntu 18.04特殊处理
    if [[ "$UBUNTU_18" == true ]]; then
        print_message "使用Ubuntu 18.04优化安装方式"
        
        # 移除旧版本
        sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
        
        # 添加Docker官方GPG密钥
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        
        # 添加Docker仓库
        sudo add-apt-repository \
           "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
           $(lsb_release -cs) \
           stable"
        
        # 更新包索引
        sudo apt-get update
        
        # 安装Docker CE
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    else
        # 使用官方安装脚本
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        rm get-docker.sh
    fi
    
    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 配置Docker镜像源 (如果需要)
    if [[ "$USE_MIRROR" == true ]]; then
        configure_docker_mirror
    fi
    
    print_message "✅ Docker安装完成"
}

# 配置Docker镜像源
configure_docker_mirror() {
    print_step "配置Docker镜像源..."
    
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://mirror.baidubce.com"
  ]
}
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl restart docker
    
    print_message "✅ Docker镜像源配置完成"
}

# 安装Docker Compose
install_docker_compose() {
    print_step "安装Docker Compose..."
    
    if command -v docker-compose &> /dev/null; then
        print_message "Docker Compose已安装: $(docker-compose --version)"
        return 0
    fi
    
    # 获取最新版本
    COMPOSE_VERSION="2.20.0"
    
    # 下载并安装
    sudo curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    # 验证安装
    if docker-compose --version; then
        print_message "✅ Docker Compose安装完成"
    else
        print_error "❌ Docker Compose安装失败"
        exit 1
    fi
}

# 配置用户权限
configure_docker_permissions() {
    print_step "配置Docker用户权限..."
    
    # 添加用户到docker组
    sudo usermod -aG docker $USER
    
    # 检查是否需要重新登录
    if ! groups $USER | grep -q docker; then
        print_warning "需要重新登录以获取docker组权限"
        print_message "请运行: newgrp docker"
        
        # 临时获取权限
        newgrp docker << EONG
        print_message "✅ 临时获取docker权限成功"
EONG
    fi
    
    print_message "✅ Docker权限配置完成"
}

# 检查系统资源
check_resources() {
    print_step "检查系统资源..."
    
    # 检查内存
    total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ "$total_mem" -ge 4096 ]; then
        print_message "✅ 内存充足: ${total_mem}MB"
    elif [ "$total_mem" -ge 2048 ]; then
        print_warning "⚠️ 内存较少: ${total_mem}MB (建议4GB以上)"
    else
        print_error "❌ 内存不足: ${total_mem}MB (最少需要2GB)"
        exit 1
    fi
    
    # 检查磁盘空间
    disk_space=$(df -h . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "${disk_space%.*}" -ge 10 ]; then
        print_message "✅ 磁盘空间充足: ${disk_space}G"
    else
        print_warning "⚠️ 磁盘空间较少: ${disk_space}G (建议10GB以上)"
    fi
    
    # 检查CPU
    cpu_cores=$(nproc)
    print_message "✅ CPU核心数: ${cpu_cores}核"
}

# 检查端口占用
check_ports() {
    print_step "检查端口占用..."
    
    ports=(80 443 8088 6379 9090)
    for port in "${ports[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            print_warning "⚠️ 端口 $port 已被占用"
            
            # 尝试识别占用进程
            process=$(sudo netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | head -1)
            if [ -n "$process" ]; then
                print_warning "   占用进程: $process"
            fi
        else
            print_message "✅ 端口 $port 可用"
        fi
    done
}

# 主函数
main() {
    print_message "智能问答系统Ubuntu 18.04优化部署脚本 v1.0"
    print_message "================================================"
    
    # 检查是否为root用户
    if [[ $EUID -eq 0 ]]; then
        print_error "请不要使用root用户运行此脚本"
        exit 1
    fi
    
    check_system
    check_network
    check_resources
    check_ports
    update_system
    install_docker
    install_docker_compose
    configure_docker_permissions
    
    print_message "✅ 环境准备完成！"
    print_message "下一步请运行: ./deploy.sh"
}

# 错误处理
trap 'print_error "脚本执行过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
