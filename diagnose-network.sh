#!/bin/bash

# 网络诊断脚本 - 诊断Docker构建环境的网络连接问题

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

# 检查基本网络连接
check_basic_connectivity() {
    print_step "检查基本网络连接..."
    
    local test_sites=(
        "www.baidu.com"
        "www.google.com"
        "github.com"
    )
    
    for site in "${test_sites[@]}"; do
        if ping -c 3 -W 5 "$site" >/dev/null 2>&1; then
            print_message "✅ $site 连接正常"
        else
            print_warning "⚠️ $site 连接失败"
        fi
    done
}

# 检查DNS解析
check_dns_resolution() {
    print_step "检查DNS解析..."
    
    local dns_servers=(
        "8.8.8.8"
        "223.5.5.5"
        "114.114.114.114"
    )
    
    for dns in "${dns_servers[@]}"; do
        if nslookup pypi.tuna.tsinghua.edu.cn "$dns" >/dev/null 2>&1; then
            print_message "✅ DNS服务器 $dns 解析正常"
        else
            print_warning "⚠️ DNS服务器 $dns 解析失败"
        fi
    done
}

# 检查PyPI镜像源连接
check_pypi_mirrors() {
    print_step "检查PyPI镜像源连接..."
    
    local mirrors=(
        "https://pypi.tuna.tsinghua.edu.cn/simple/"
        "https://mirrors.aliyun.com/pypi/simple/"
        "https://pypi.mirrors.ustc.edu.cn/simple/"
        "https://pypi.douban.com/simple/"
        "https://mirror.baidu.com/pypi/simple/"
    )
    
    for mirror in "${mirrors[@]}"; do
        print_message "测试镜像源: $mirror"
        
        # 测试连接速度
        local start_time=$(date +%s.%N)
        if curl -I --connect-timeout 10 --max-time 30 "$mirror" >/dev/null 2>&1; then
            local end_time=$(date +%s.%N)
            local duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")
            print_message "✅ $mirror 连接成功 (耗时: ${duration}s)"
        else
            print_warning "⚠️ $mirror 连接失败"
        fi
    done
}

# 检查Docker网络配置
check_docker_network() {
    print_step "检查Docker网络配置..."
    
    # 检查Docker daemon配置
    if [ -f /etc/docker/daemon.json ]; then
        print_message "Docker daemon配置:"
        cat /etc/docker/daemon.json
    else
        print_warning "未找到Docker daemon配置文件"
    fi
    
    # 检查Docker代理配置
    if [ -f /etc/systemd/system/docker.service.d/http-proxy.conf ]; then
        print_message "Docker代理配置:"
        cat /etc/systemd/system/docker.service.d/http-proxy.conf
    else
        print_warning "未找到Docker代理配置"
    fi
}

# 检查代理设置
check_proxy_settings() {
    print_step "检查代理设置..."
    
    local proxy_vars=(
        "HTTP_PROXY"
        "HTTPS_PROXY"
        "http_proxy"
        "https_proxy"
        "NO_PROXY"
        "no_proxy"
    )
    
    for var in "${proxy_vars[@]}"; do
        if [ -n "${!var}" ]; then
            print_message "$var = ${!var}"
        else
            print_warning "$var 未设置"
        fi
    done
}

# 测试pip安装
test_pip_install() {
    print_step "测试pip安装..."
    
    local mirrors=(
        "https://pypi.tuna.tsinghua.edu.cn/simple"
        "https://mirrors.aliyun.com/pypi/simple/"
        "https://pypi.mirrors.ustc.edu.cn/simple/"
    )
    
    for mirror in "${mirrors[@]}"; do
        print_message "测试pip安装 (镜像源: $mirror)..."
        
        # 在临时容器中测试pip安装
        if docker run --rm \
            --env HTTP_PROXY="$HTTP_PROXY" \
            --env HTTPS_PROXY="$HTTPS_PROXY" \
            --env NO_PROXY="$NO_PROXY" \
            python:3.9-slim-bullseye \
            pip install --no-cache-dir --timeout=30 --retries=2 \
            -i "$mirror" requests==2.31.0 >/dev/null 2>&1; then
            print_message "✅ $mirror pip安装测试成功"
        else
            print_warning "⚠️ $mirror pip安装测试失败"
        fi
    done
}

# 生成诊断报告
generate_report() {
    print_step "生成诊断报告..."
    
    local report_file="network_diagnosis_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "网络诊断报告"
        echo "生成时间: $(date)"
        echo "=========================="
        echo
        
        echo "系统信息:"
        uname -a
        echo
        
        echo "网络接口:"
        ip addr show
        echo
        
        echo "路由表:"
        ip route show
        echo
        
        echo "DNS配置:"
        cat /etc/resolv.conf
        echo
        
        echo "代理环境变量:"
        env | grep -i proxy || echo "无代理配置"
        echo
        
    } > "$report_file"
    
    print_message "诊断报告已保存到: $report_file"
}

# 提供解决建议
provide_suggestions() {
    print_step "解决建议..."
    
    echo
    print_message "=== 常见解决方案 ==="
    echo
    echo "1. 如果所有镜像源都连接失败："
    echo "   - 检查网络连接是否正常"
    echo "   - 确认防火墙设置"
    echo "   - 尝试使用代理服务器"
    echo
    echo "2. 如果部分镜像源失败："
    echo "   - 使用连接成功的镜像源"
    echo "   - 在Dockerfile中调整镜像源顺序"
    echo
    echo "3. 如果Docker构建超时："
    echo "   - 增加超时时间"
    echo "   - 减少并发连接数"
    echo "   - 使用Docker构建缓存"
    echo
    echo "4. 代理环境问题："
    echo "   - 确认代理服务器地址正确"
    echo "   - 检查代理认证信息"
    echo "   - 配置Docker daemon代理"
    echo
}

# 主函数
main() {
    print_message "Docker构建网络诊断工具 v1.0"
    print_message "================================"
    
    check_proxy_settings
    check_basic_connectivity
    check_dns_resolution
    check_pypi_mirrors
    check_docker_network
    test_pip_install
    generate_report
    provide_suggestions
    
    print_message "✅ 网络诊断完成！"
}

# 错误处理
trap 'print_error "诊断过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
