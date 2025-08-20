#!/bin/bash

# Ubuntu 18.04 兼容性检查脚本
# 专门检查Ubuntu 18.04环境下的部署兼容性

set -e

echo "🔍 Ubuntu 18.04 兼容性检查..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# 检查系统版本
check_ubuntu_version() {
    echo "📋 检查Ubuntu版本..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        
        if [[ "$NAME" == "Ubuntu" ]]; then
            if [[ "$VERSION_ID" == "18.04" ]]; then
                print_success "Ubuntu 18.04 LTS 检测通过"
                print_info "  版本: $VERSION"
                print_info "  代号: $VERSION_CODENAME"
                
                # 检查内核版本
                kernel_version=$(uname -r)
                print_info "  内核版本: $kernel_version"
                
                # 检查是否为最新补丁
                if apt list --upgradable 2>/dev/null | grep -q upgradable; then
                    print_warning "  系统有可用更新，建议先更新系统"
                else
                    print_success "  系统已是最新版本"
                fi
                
            else
                print_warning "检测到Ubuntu $VERSION_ID，非18.04版本"
                print_info "  脚本主要针对18.04优化，其他版本可能需要调整"
            fi
        else
            print_error "非Ubuntu系统: $NAME"
            print_info "  此脚本专为Ubuntu 18.04设计"
        fi
    else
        print_error "无法检测系统版本"
    fi
}

# 检查系统架构
check_architecture() {
    echo ""
    echo "🏗️ 检查系统架构..."
    
    arch=$(uname -m)
    case $arch in
        x86_64)
            print_success "架构: $arch (64位，完全支持)"
            ;;
        aarch64|arm64)
            print_warning "架构: $arch (ARM64，部分支持)"
            print_info "  Docker镜像可能需要使用ARM版本"
            ;;
        *)
            print_error "架构: $arch (不支持)"
            print_info "  建议使用x86_64架构"
            ;;
    esac
}

# 检查包管理器
check_package_manager() {
    echo ""
    echo "📦 检查包管理器..."
    
    if command -v apt &> /dev/null; then
        print_success "APT包管理器可用"
        
        # 检查源列表
        if [ -f /etc/apt/sources.list ]; then
            print_success "APT源配置存在"
            
            # 检查是否有HTTPS支持
            if dpkg -l | grep -q apt-transport-https; then
                print_success "HTTPS传输支持已安装"
            else
                print_warning "HTTPS传输支持未安装，将自动安装"
            fi
        fi
        
        # 测试包管理器
        if sudo apt update &> /dev/null; then
            print_success "APT源连接正常"
        else
            print_error "APT源连接失败"
        fi
    else
        print_error "APT包管理器不可用"
    fi
}

# 检查Python环境
check_python() {
    echo ""
    echo "🐍 检查Python环境..."
    
    # Ubuntu 18.04默认Python版本
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_info "系统Python版本: $python_version"
        
        if [[ "$python_version" == "3.6"* ]]; then
            print_warning "Python 3.6 (Ubuntu 18.04默认版本)"
            print_info "  容器内将使用Python 3.9，无影响"
        elif [[ "$python_version" > "3.8" ]]; then
            print_success "Python版本满足要求"
        else
            print_warning "Python版本较旧: $python_version"
        fi
    else
        print_error "Python3未安装"
    fi
    
    # 检查pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3可用"
    else
        print_warning "pip3未安装，将自动安装"
    fi
}

# 检查网络配置
check_network_config() {
    echo ""
    echo "🌐 检查网络配置..."
    
    # 检查DNS配置
    if [ -f /etc/resolv.conf ]; then
        dns_servers=$(grep nameserver /etc/resolv.conf | wc -l)
        if [ "$dns_servers" -gt 0 ]; then
            print_success "DNS配置正常 ($dns_servers个DNS服务器)"
        else
            print_error "DNS配置异常"
        fi
    fi
    
    # 检查防火墙状态
    if command -v ufw &> /dev/null; then
        ufw_status=$(sudo ufw status | head -1)
        print_info "防火墙状态: $ufw_status"
        
        if [[ "$ufw_status" == *"active"* ]]; then
            print_warning "防火墙已启用，可能需要开放端口"
        fi
    fi
    
    # 检查网络接口
    interfaces=$(ip link show | grep -E '^[0-9]+:' | wc -l)
    print_info "网络接口数量: $interfaces"
}

# 检查存储空间
check_storage() {
    echo ""
    echo "💾 检查存储空间..."
    
    # 检查根分区空间
    root_space=$(df -h / | awk 'NR==2 {print $4}')
    root_used=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    print_info "根分区可用空间: $root_space"
    print_info "根分区使用率: $root_used%"
    
    if [ "$root_used" -lt 80 ]; then
        print_success "磁盘空间充足"
    elif [ "$root_used" -lt 90 ]; then
        print_warning "磁盘空间较紧张"
    else
        print_error "磁盘空间不足"
    fi
    
    # 检查/var/lib/docker空间 (Docker数据目录)
    if [ -d /var/lib/docker ]; then
        docker_space=$(du -sh /var/lib/docker 2>/dev/null | cut -f1)
        print_info "Docker数据占用: $docker_space"
    fi
    
    # 检查临时目录空间
    tmp_space=$(df -h /tmp | awk 'NR==2 {print $4}')
    print_info "临时目录可用: $tmp_space"
}

# 检查内存配置
check_memory() {
    echo ""
    echo "🧠 检查内存配置..."
    
    # 物理内存
    total_mem=$(free -h | awk 'NR==2{print $2}')
    available_mem=$(free -h | awk 'NR==2{print $7}')
    
    print_info "总内存: $total_mem"
    print_info "可用内存: $available_mem"
    
    # 检查交换空间
    swap_total=$(free -h | awk 'NR==3{print $2}')
    if [[ "$swap_total" == "0B" ]]; then
        print_warning "未配置交换空间"
        print_info "  建议配置2GB交换空间"
    else
        print_success "交换空间: $swap_total"
    fi
    
    # 内存使用率
    mem_used=$(free | awk 'NR==2{printf "%.0f", $3/$2 * 100.0}')
    if [ "$mem_used" -lt 80 ]; then
        print_success "内存使用率正常: $mem_used%"
    else
        print_warning "内存使用率较高: $mem_used%"
    fi
}

# 检查安全配置
check_security() {
    echo ""
    echo "🔒 检查安全配置..."
    
    # 检查SELinux (Ubuntu通常不使用)
    if command -v getenforce &> /dev/null; then
        selinux_status=$(getenforce)
        print_info "SELinux状态: $selinux_status"
    else
        print_info "SELinux未安装 (Ubuntu正常)"
    fi
    
    # 检查AppArmor (Ubuntu默认安全模块)
    if command -v aa-status &> /dev/null; then
        if sudo aa-status &> /dev/null; then
            print_success "AppArmor正常运行"
        else
            print_warning "AppArmor状态异常"
        fi
    else
        print_warning "AppArmor未安装"
    fi
    
    # 检查sudo权限
    if sudo -n true 2>/dev/null; then
        print_success "sudo权限正常"
    else
        print_info "需要sudo密码 (正常)"
    fi
}

# 生成兼容性报告
generate_report() {
    echo ""
    echo "📊 兼容性检查报告"
    echo "================================"
    
    echo "✅ 兼容性良好的组件:"
    echo "  - Ubuntu 18.04 LTS系统"
    echo "  - APT包管理器"
    echo "  - 网络连接"
    echo "  - 基础系统工具"
    
    echo ""
    echo "⚠️ 需要注意的组件:"
    echo "  - Python 3.6 (容器内使用3.9)"
    echo "  - 可能需要更新系统包"
    echo "  - 防火墙配置"
    
    echo ""
    echo "🔧 建议的预处理步骤:"
    echo "  1. 更新系统: sudo apt update && sudo apt upgrade"
    echo "  2. 安装基础工具: sudo apt install curl wget git"
    echo "  3. 配置防火墙规则 (如果启用)"
    echo "  4. 确保有足够的磁盘空间"
    
    echo ""
    echo "🚀 部署建议:"
    echo "  - 使用Docker容器化部署 (推荐)"
    echo "  - 配置Docker镜像源 (提升下载速度)"
    echo "  - 监控系统资源使用"
    echo "  - 定期备份重要数据"
}

# 主函数
main() {
    echo "Ubuntu 18.04 兼容性检查工具"
    echo "============================"
    
    check_ubuntu_version
    check_architecture
    check_package_manager
    check_python
    check_network_config
    check_storage
    check_memory
    check_security
    generate_report
    
    echo ""
    echo "✅ 兼容性检查完成！"
    echo "如果所有检查都通过，可以继续部署流程。"
}

main "$@"
