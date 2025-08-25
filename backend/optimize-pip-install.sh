#!/bin/bash

# pip安装优化脚本 - 专门解决代理环境下的pip安装超时问题
# 适用于Docker构建环境

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

# 配置多个国内镜像源
configure_pip_mirrors() {
    print_step "配置pip镜像源..."
    
    mkdir -p /root/.pip
    
    cat > /root/.pip/pip.conf << 'EOF'
[global]
# 主镜像源 - 清华大学
index-url = https://pypi.tuna.tsinghua.edu.cn/simple

# 备用镜像源
extra-index-url = https://mirrors.aliyun.com/pypi/simple/
                  https://pypi.mirrors.ustc.edu.cn/simple/
                  https://pypi.douban.com/simple/
                  https://mirror.baidu.com/pypi/simple/

# 信任的主机
trusted-host = pypi.tuna.tsinghua.edu.cn
               mirrors.aliyun.com
               pypi.mirrors.ustc.edu.cn
               pypi.douban.com
               mirror.baidu.com

# 超时和重试配置
timeout = 120
retries = 5
default-timeout = 120

# 缓存配置
cache-dir = /tmp/pip-cache
EOF

    print_message "✅ pip配置文件已创建"
}

# 测试网络连通性
test_network_connectivity() {
    print_step "测试网络连通性..."
    
    local mirrors=(
        "https://pypi.tuna.tsinghua.edu.cn/simple/"
        "https://mirrors.aliyun.com/pypi/simple/"
        "https://pypi.mirrors.ustc.edu.cn/simple/"
        "https://pypi.douban.com/simple/"
    )
    
    local working_mirrors=()
    
    for mirror in "${mirrors[@]}"; do
        print_message "测试镜像源: $mirror"
        if curl -I --connect-timeout 10 --max-time 30 "$mirror" >/dev/null 2>&1; then
            print_message "✅ $mirror 连接成功"
            working_mirrors+=("$mirror")
        else
            print_warning "⚠️ $mirror 连接失败"
        fi
    done
    
    if [ ${#working_mirrors[@]} -eq 0 ]; then
        print_error "所有镜像源都无法连接！"
        return 1
    fi
    
    print_message "✅ 可用镜像源数量: ${#working_mirrors[@]}"
    return 0
}

# 优化DNS设置
optimize_dns() {
    print_step "优化DNS设置..."
    
    # 备份原始DNS配置
    cp /etc/resolv.conf /etc/resolv.conf.backup
    
    # 添加国内DNS服务器
    cat > /etc/resolv.conf << 'EOF'
# 阿里云DNS
nameserver 223.5.5.5
nameserver 223.6.6.6
# 腾讯DNS
nameserver 119.29.29.29
nameserver 182.254.116.116
# 百度DNS
nameserver 180.76.76.76
# Google DNS (备用)
nameserver 8.8.8.8
nameserver 8.8.4.4
EOF
    
    print_message "✅ DNS配置已优化"
}

# 安装基础依赖
install_basic_deps() {
    print_step "安装基础Python包..."
    
    local basic_packages=(
        "pip>=23.0"
        "setuptools>=65.0"
        "wheel>=0.38.0"
    )
    
    for package in "${basic_packages[@]}"; do
        print_message "安装: $package"
        pip install --no-cache-dir --timeout=120 --retries=5 \
            -i https://pypi.tuna.tsinghua.edu.cn/simple \
            --upgrade "$package" || {
            print_warning "使用备用镜像源重试..."
            pip install --no-cache-dir --timeout=120 --retries=5 \
                -i https://mirrors.aliyun.com/pypi/simple/ \
                --upgrade "$package"
        }
    done
    
    print_message "✅ 基础依赖安装完成"
}

# 分批安装requirements.txt中的依赖
install_requirements_batch() {
    print_step "分批安装requirements.txt依赖..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt文件不存在！"
        return 1
    fi
    
    # 定义依赖分组（按重要性和依赖关系）
    local core_deps=(
        "Flask==2.3.2"
        "werkzeug==2.3.7"
        "SQLAlchemy==2.0.19"
    )
    
    local db_deps=(
        "psycopg2-binary==2.9.7"
        "Flask-SQLAlchemy==3.0.5"
    )
    
    local web_deps=(
        "Flask-CORS==4.0.0"
        "Flask-RESTful==0.3.10"
        "flask-restx==1.1.0"
        "Flask-JWT-Extended==4.5.2"
    )
    
    local util_deps=(
        "requests==2.31.0"
        "python-dotenv==1.0.0"
        "APScheduler==3.10.1"
        "colorlog==6.7.0"
        "marshmallow==3.20.1"
        "python-dateutil==2.8.2"
        "pytz==2023.3"
        "jieba==0.42.1"
    )
    
    local data_deps=(
        "numpy==1.24.3"
        "pandas==2.0.3"
        "openpyxl==3.1.2"
    )
    
    local dev_deps=(
        "pytest==7.4.0"
        "pytest-flask==1.2.0"
        "black==23.7.0"
        "flake8==6.1.0"
    )
    
    local prod_deps=(
        "gunicorn==21.2.0"
    )
    
    # 按组安装
    local groups=(
        "core_deps[@]"
        "db_deps[@]"
        "web_deps[@]"
        "util_deps[@]"
        "data_deps[@]"
        "dev_deps[@]"
        "prod_deps[@]"
    )
    
    local group_names=(
        "核心框架"
        "数据库"
        "Web组件"
        "工具库"
        "数据处理"
        "开发工具"
        "生产服务器"
    )
    
    for i in "${!groups[@]}"; do
        local group_name="${group_names[$i]}"
        local group_ref="${groups[$i]}"
        
        print_step "安装 $group_name 依赖..."
        
        # 使用间接引用获取数组
        local -n group_packages=$group_ref
        
        for package in "${group_packages[@]}"; do
            print_message "安装: $package"
            
            # 尝试主镜像源
            if ! pip install --no-cache-dir --timeout=120 --retries=3 \
                -i https://pypi.tuna.tsinghua.edu.cn/simple \
                "$package"; then
                
                print_warning "主镜像源失败，尝试备用镜像源..."
                
                # 尝试备用镜像源
                local backup_mirrors=(
                    "https://mirrors.aliyun.com/pypi/simple/"
                    "https://pypi.mirrors.ustc.edu.cn/simple/"
                    "https://pypi.douban.com/simple/"
                )
                
                local installed=false
                for mirror in "${backup_mirrors[@]}"; do
                    if pip install --no-cache-dir --timeout=120 --retries=3 \
                        -i "$mirror" "$package"; then
                        installed=true
                        break
                    fi
                done
                
                if [ "$installed" = false ]; then
                    print_error "无法安装 $package，所有镜像源都失败了"
                    return 1
                fi
            fi
        done
        
        print_message "✅ $group_name 依赖安装完成"
        sleep 2  # 短暂休息，避免过于频繁的请求
    done
}

# 验证安装结果
verify_installation() {
    print_step "验证安装结果..."
    
    local test_imports=(
        "flask:Flask"
        "sqlalchemy:SQLAlchemy"
        "psycopg2:psycopg2"
        "requests:requests"
        "gunicorn:gunicorn"
    )
    
    for test in "${test_imports[@]}"; do
        local module="${test%:*}"
        local import_name="${test#*:}"
        
        if python -c "import $module; print(f'✅ $import_name: OK')" 2>/dev/null; then
            print_message "✅ $import_name 导入成功"
        else
            print_error "❌ $import_name 导入失败"
            return 1
        fi
    done
    
    print_message "✅ 所有关键依赖验证通过"
}

# 清理缓存
cleanup_cache() {
    print_step "清理pip缓存..."
    
    pip cache purge 2>/dev/null || true
    rm -rf /tmp/pip-cache 2>/dev/null || true
    rm -rf /root/.cache/pip 2>/dev/null || true
    
    print_message "✅ 缓存清理完成"
}

# 主函数
main() {
    print_message "pip安装优化脚本 v1.0"
    print_message "=========================="
    
    # 检查是否在Docker环境中
    if [ -f /.dockerenv ]; then
        print_message "检测到Docker环境"
    fi
    
    # 显示代理配置
    if [ -n "$HTTP_PROXY" ]; then
        print_message "HTTP代理: $HTTP_PROXY"
    fi
    if [ -n "$HTTPS_PROXY" ]; then
        print_message "HTTPS代理: $HTTPS_PROXY"
    fi
    
    # 执行优化步骤
    optimize_dns
    configure_pip_mirrors
    test_network_connectivity
    install_basic_deps
    install_requirements_batch
    verify_installation
    cleanup_cache
    
    print_message "✅ pip安装优化完成！"
}

# 错误处理
trap 'print_error "脚本执行过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
