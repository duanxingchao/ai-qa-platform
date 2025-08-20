#!/bin/bash

# 代理环境配置脚本
# 用于在有内网代理的环境中配置所有必要的代理设置

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

# 获取代理配置
get_proxy_config() {
    print_step "配置代理服务器..."
    
    if [[ -z "$PROXY_SERVER" ]]; then
        echo -n "请输入代理服务器地址 (格式: http://proxy-server:port): "
        read PROXY_SERVER
    fi
    
    if [[ -z "$PROXY_SERVER" ]]; then
        print_error "代理服务器地址不能为空"
        exit 1
    fi
    
    # 验证代理地址格式
    if [[ ! "$PROXY_SERVER" =~ ^https?:// ]]; then
        print_error "代理地址格式错误，应该以 http:// 或 https:// 开头"
        exit 1
    fi
    
    print_message "使用代理服务器: $PROXY_SERVER"
    
    # 询问是否需要认证
    echo -n "代理服务器是否需要用户名密码认证? (y/n): "
    read need_auth
    
    if [[ "$need_auth" == "y" ]] || [[ "$need_auth" == "Y" ]]; then
        echo -n "请输入用户名: "
        read proxy_username
        echo -n "请输入密码: "
        read -s proxy_password
        echo
        
        # 构建带认证的代理URL
        PROXY_WITH_AUTH=$(echo "$PROXY_SERVER" | sed "s|://|://${proxy_username}:${proxy_password}@|")
        PROXY_SERVER="$PROXY_WITH_AUTH"
    fi
}

# 配置系统环境变量
configure_system_proxy() {
    print_step "配置系统代理环境变量..."
    
    # 设置当前会话的代理
    export http_proxy="$PROXY_SERVER"
    export https_proxy="$PROXY_SERVER"
    export HTTP_PROXY="$PROXY_SERVER"
    export HTTPS_PROXY="$PROXY_SERVER"
    export no_proxy="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
    export NO_PROXY="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
    
    # 添加到 ~/.bashrc
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
        print_message "✅ 代理配置已添加到 ~/.bashrc"
    else
        print_message "✅ ~/.bashrc 中已存在代理配置"
    fi
}

# 配置APT代理
configure_apt_proxy() {
    print_step "配置APT包管理器代理..."
    
    sudo tee /etc/apt/apt.conf.d/95proxies > /dev/null << EOF
Acquire::http::Proxy "$PROXY_SERVER";
Acquire::https::Proxy "$PROXY_SERVER";
EOF
    
    print_message "✅ APT代理配置完成"
}

# 配置Git代理
configure_git_proxy() {
    print_step "配置Git代理..."
    
    git config --global http.proxy "$PROXY_SERVER"
    git config --global https.proxy "$PROXY_SERVER"
    
    print_message "✅ Git代理配置完成"
}

# 配置npm代理（如果存在）
configure_npm_proxy() {
    if command -v npm &> /dev/null; then
        print_step "配置npm代理..."
        
        npm config set proxy "$PROXY_SERVER"
        npm config set https-proxy "$PROXY_SERVER"
        npm config set registry https://registry.npmmirror.com/
        
        print_message "✅ npm代理配置完成"
    fi
}

# 配置yarn代理（如果存在）
configure_yarn_proxy() {
    if command -v yarn &> /dev/null; then
        print_step "配置yarn代理..."
        
        yarn config set proxy "$PROXY_SERVER"
        yarn config set https-proxy "$PROXY_SERVER"
        yarn config set registry https://registry.npmmirror.com/
        
        print_message "✅ yarn代理配置完成"
    fi
}

# 测试代理连接
test_proxy_connection() {
    print_step "测试代理连接..."
    
    # 测试HTTP连接
    if curl -s --connect-timeout 10 --proxy "$PROXY_SERVER" http://www.google.com > /dev/null; then
        print_message "✅ HTTP代理连接测试成功"
    else
        print_warning "⚠️ HTTP代理连接测试失败"
    fi
    
    # 测试HTTPS连接
    if curl -s --connect-timeout 10 --proxy "$PROXY_SERVER" https://www.google.com > /dev/null; then
        print_message "✅ HTTPS代理连接测试成功"
    else
        print_warning "⚠️ HTTPS代理连接测试失败"
    fi
    
    # 测试Docker Hub连接
    if curl -s --connect-timeout 10 --proxy "$PROXY_SERVER" https://hub.docker.com > /dev/null; then
        print_message "✅ Docker Hub代理连接测试成功"
    else
        print_warning "⚠️ Docker Hub代理连接测试失败"
    fi
}

# 创建代理配置文件
create_proxy_config_file() {
    print_step "创建代理配置文件..."
    
    cat > .proxy-config << EOF
# 代理配置文件
# 由 setup-proxy-environment.sh 生成

PROXY_SERVER="$PROXY_SERVER"
http_proxy="$PROXY_SERVER"
https_proxy="$PROXY_SERVER"
HTTP_PROXY="$PROXY_SERVER"
HTTPS_PROXY="$PROXY_SERVER"
no_proxy="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
NO_PROXY="localhost,127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"

# 使用方法：
# source .proxy-config
EOF
    
    print_message "✅ 代理配置文件已创建: .proxy-config"
}

# 显示使用说明
show_usage_instructions() {
    print_step "代理配置完成！"
    
    echo
    print_message "=== 使用说明 ==="
    echo "1. 重新加载环境变量："
    echo "   source ~/.bashrc"
    echo
    echo "2. 或者加载代理配置文件："
    echo "   source .proxy-config"
    echo
    echo "3. 验证代理配置："
    echo "   echo \$http_proxy"
    echo "   curl -I https://www.google.com"
    echo
    echo "4. 现在可以运行部署脚本："
    echo "   ./deploy-ubuntu18.sh"
    echo
}

# 主函数
main() {
    print_message "代理环境配置脚本 v1.0"
    print_message "=========================="
    
    get_proxy_config
    configure_system_proxy
    configure_apt_proxy
    configure_git_proxy
    configure_npm_proxy
    configure_yarn_proxy
    test_proxy_connection
    create_proxy_config_file
    show_usage_instructions
    
    print_message "✅ 代理环境配置完成！"
}

# 错误处理
trap 'print_error "脚本执行过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
