#!/bin/bash

# 端口冲突检查脚本
# 检查当前端口占用情况并推荐安全的端口配置

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

# 检查当前配置的端口
check_current_ports() {
    print_header "检查当前配置端口占用情况"
    
    # 当前配置的端口
    current_ports=(80 443 6379 8088 9090)
    
    echo "当前项目配置的端口："
    echo "├── 80   - 前端HTTP"
    echo "├── 443  - 前端HTTPS"
    echo "├── 6379 - Redis缓存"
    echo "├── 8088 - 后端API"
    echo "└── 9090 - Prometheus监控"
    echo
    
    conflict_count=0
    
    for port in "${current_ports[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            print_error "❌ 端口 $port 已被占用"
            
            # 尝试识别占用进程
            if command -v ss &> /dev/null; then
                process=$(ss -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | head -1)
            else
                process=$(sudo netstat -tulnp 2>/dev/null | grep ":$port " | awk '{print $7}' | head -1)
            fi
            
            if [ -n "$process" ]; then
                echo "   占用进程: $process"
            fi
            
            # 根据端口给出具体建议
            case $port in
                80)
                    echo "   建议: 端口80通常被Nginx/Apache占用，必须更换"
                    ;;
                443)
                    echo "   建议: 端口443通常被HTTPS服务占用，必须更换"
                    ;;
                6379)
                    echo "   建议: 端口6379是Redis默认端口，可能与现有Redis冲突"
                    ;;
                8088)
                    echo "   建议: 端口8088相对安全，但仍建议检查占用进程"
                    ;;
                9090)
                    echo "   建议: 端口9090常用于监控服务，可能冲突"
                    ;;
            esac
            
            conflict_count=$((conflict_count + 1))
        else
            print_message "✅ 端口 $port 可用"
        fi
        echo
    done
    
    if [ $conflict_count -gt 0 ]; then
        print_warning "发现 $conflict_count 个端口冲突，强烈建议修改端口配置！"
    else
        print_message "所有端口都可用，但仍建议使用企业级端口配置"
    fi
}

# 检查推荐端口
check_recommended_ports() {
    print_header "检查推荐端口可用性"
    
    # 推荐端口方案
    echo "推荐端口方案："
    echo
    echo "方案一 - 企业标准端口 (18xxx系列):"
    echo "├── 18080 - 前端HTTP"
    echo "├── 18443 - 前端HTTPS"
    echo "├── 18088 - 后端API"
    echo "├── 16379 - Redis缓存"
    echo "└── 19090 - Prometheus监控"
    echo
    
    recommended_ports_1=(18080 18443 18088 16379 19090)
    available_1=0
    
    for port in "${recommended_ports_1[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            print_warning "⚠️ 推荐端口 $port 已被占用"
        else
            print_message "✅ 推荐端口 $port 可用"
            available_1=$((available_1 + 1))
        fi
    done
    
    echo
    echo "方案二 - 高端口段 (28xxx系列):"
    echo "├── 28080 - 前端HTTP"
    echo "├── 28443 - 前端HTTPS"
    echo "├── 28088 - 后端API"
    echo "├── 26379 - Redis缓存"
    echo "└── 29090 - Prometheus监控"
    echo
    
    recommended_ports_2=(28080 28443 28088 26379 29090)
    available_2=0
    
    for port in "${recommended_ports_2[@]}"; do
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            print_warning "⚠️ 高端口 $port 已被占用"
        else
            print_message "✅ 高端口 $port 可用"
            available_2=$((available_2 + 1))
        fi
    done
    
    echo
    if [ $available_1 -eq 5 ]; then
        print_message "🎯 推荐使用方案一 (18xxx系列) - 所有端口都可用"
        RECOMMENDED_SCHEME="scheme1"
    elif [ $available_2 -eq 5 ]; then
        print_message "🎯 推荐使用方案二 (28xxx系列) - 所有端口都可用"
        RECOMMENDED_SCHEME="scheme2"
    elif [ $available_1 -gt $available_2 ]; then
        print_message "🎯 推荐使用方案一 (18xxx系列) - 可用端口更多"
        RECOMMENDED_SCHEME="scheme1"
    else
        print_message "🎯 推荐使用方案二 (28xxx系列) - 可用端口更多"
        RECOMMENDED_SCHEME="scheme2"
    fi
}

# 检查常用服务端口
check_common_service_ports() {
    print_header "检查常用服务端口占用"
    
    common_services=(
        "22:SSH"
        "25:SMTP"
        "53:DNS"
        "80:HTTP"
        "110:POP3"
        "143:IMAP"
        "443:HTTPS"
        "993:IMAPS"
        "995:POP3S"
        "3306:MySQL"
        "5432:PostgreSQL"
        "6379:Redis"
        "8080:HTTP-Alt"
        "9090:Prometheus"
        "27017:MongoDB"
    )
    
    echo "常用服务端口占用情况："
    
    for service in "${common_services[@]}"; do
        port=$(echo $service | cut -d: -f1)
        name=$(echo $service | cut -d: -f2)
        
        if netstat -tuln 2>/dev/null | grep -q ":$port "; then
            echo "❌ $port ($name) - 已占用"
        else
            echo "✅ $port ($name) - 可用"
        fi
    done
}

# 生成端口配置文件
generate_port_config() {
    print_header "生成推荐端口配置"
    
    if [ "$RECOMMENDED_SCHEME" = "scheme1" ]; then
        cat > .port-config << EOF
# 推荐端口配置 - 企业标准端口 (18xxx系列)
# 由 check-ports.sh 生成

FRONTEND_HTTP_PORT=18080
FRONTEND_HTTPS_PORT=18443
BACKEND_API_PORT=18088
REDIS_PORT=16379
PROMETHEUS_PORT=19090

# Docker Compose端口映射
DOCKER_FRONTEND_HTTP="18080:80"
DOCKER_FRONTEND_HTTPS="18443:443"
DOCKER_BACKEND_API="18088:8088"
DOCKER_REDIS="16379:6379"
DOCKER_PROMETHEUS="19090:9090"

# 访问地址
FRONTEND_URL="http://\${SERVER_IP}:18080"
BACKEND_URL="http://\${SERVER_IP}:18088"
PROMETHEUS_URL="http://\${SERVER_IP}:19090"
EOF
        
        print_message "✅ 已生成企业标准端口配置文件: .port-config"
        
    else
        cat > .port-config << EOF
# 推荐端口配置 - 高端口段 (28xxx系列)
# 由 check-ports.sh 生成

FRONTEND_HTTP_PORT=28080
FRONTEND_HTTPS_PORT=28443
BACKEND_API_PORT=28088
REDIS_PORT=26379
PROMETHEUS_PORT=29090

# Docker Compose端口映射
DOCKER_FRONTEND_HTTP="28080:80"
DOCKER_FRONTEND_HTTPS="28443:443"
DOCKER_BACKEND_API="28088:8088"
DOCKER_REDIS="26379:6379"
DOCKER_PROMETHEUS="29090:9090"

# 访问地址
FRONTEND_URL="http://\${SERVER_IP}:28080"
BACKEND_URL="http://\${SERVER_IP}:28088"
PROMETHEUS_URL="http://\${SERVER_IP}:29090"
EOF
        
        print_message "✅ 已生成高端口段配置文件: .port-config"
    fi
}

# 显示使用说明
show_usage_instructions() {
    print_header "端口配置使用说明"
    
    echo "下一步操作："
    echo
    echo "1. 查看推荐配置："
    echo "   cat .port-config"
    echo
    echo "2. 应用端口配置："
    echo "   ./apply-port-config.sh"
    echo
    echo "3. 或手动修改 docker-compose.ubuntu18.yml 中的端口映射"
    echo
    echo "4. 重新部署服务："
    echo "   docker-compose -f docker-compose.ubuntu18.yml down"
    echo "   docker-compose -f docker-compose.ubuntu18.yml up -d"
    echo
    
    if [ -f ".port-config" ]; then
        echo "推荐配置内容："
        echo "----------------------------------------"
        cat .port-config
        echo "----------------------------------------"
    fi
}

# 主函数
main() {
    print_message "端口冲突检查脚本 v1.0"
    print_message "========================"
    
    # 检查必要工具
    if ! command -v netstat &> /dev/null && ! command -v ss &> /dev/null; then
        print_error "需要安装 netstat 或 ss 工具"
        print_message "Ubuntu/Debian: sudo apt install net-tools"
        print_message "CentOS/RHEL: sudo yum install net-tools"
        exit 1
    fi
    
    check_current_ports
    check_recommended_ports
    check_common_service_ports
    generate_port_config
    show_usage_instructions
    
    print_message "✅ 端口检查完成！"
}

# 错误处理
trap 'print_error "脚本执行过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
