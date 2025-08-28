#!/bin/bash

# 快速构建操作脚本
# 提供常用的构建操作快捷方式

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
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

# 显示菜单
show_menu() {
    echo
    print_message "=== 快速构建菜单 ==="
    echo
    echo "1. 🚀 完整构建（首次使用）"
    echo "2. ⏩ 继续构建（中断后继续）"
    echo "3. 📊 查看构建状态"
    echo "4. 🔄 重新构建后端"
    echo "5. 🎨 重新构建前端"
    echo "6. 📥 重新下载基础镜像"
    echo "7. 🧹 清理并重新开始"
    echo "8. 🔧 只配置环境（不构建）"
    echo "9. ✅ 启动服务"
    echo "10. 🛑 停止服务"
    echo "11. 📋 查看服务状态"
    echo "12. 📖 查看帮助"
    echo "0. ❌ 退出"
    echo
    echo -n "请选择操作 (0-12): "
}

# 检查脚本是否存在
check_scripts() {
    if [ ! -f "build-step-by-step.sh" ]; then
        print_error "build-step-by-step.sh 文件不存在"
        exit 1
    fi
    
    # 确保脚本有执行权限
    chmod +x build-step-by-step.sh
}

# 完整构建
full_build() {
    print_step "开始完整构建"
    ./build-step-by-step.sh
}

# 继续构建
continue_build() {
    print_step "继续构建"
    ./build-step-by-step.sh --continue
}

# 查看状态
show_status() {
    print_step "查看构建状态"
    ./build-step-by-step.sh --status
}

# 重新构建后端
rebuild_backend() {
    print_step "重新构建后端"
    ./build-step-by-step.sh --step 7
    ./build-step-by-step.sh --step 9
    ./build-step-by-step.sh --step 10
}

# 重新构建前端
rebuild_frontend() {
    print_step "重新构建前端"
    ./build-step-by-step.sh --step 8
    ./build-step-by-step.sh --step 9
    ./build-step-by-step.sh --step 10
}

# 重新下载基础镜像
redownload_images() {
    print_step "重新下载基础镜像"
    ./build-step-by-step.sh --step 6
}

# 清理并重新开始
clean_rebuild() {
    print_step "清理并重新开始"
    ./build-step-by-step.sh --reset
    ./build-step-by-step.sh
}

# 只配置环境
setup_environment() {
    print_step "配置环境"
    ./build-step-by-step.sh --step 1
    ./build-step-by-step.sh --step 2
    ./build-step-by-step.sh --step 3
    ./build-step-by-step.sh --step 4
}

# 启动服务
start_services() {
    print_step "启动服务"
    if [ -f "docker-compose.ubuntu18.yml" ]; then
        docker-compose -f docker-compose.ubuntu18.yml up -d
        print_message "服务已启动"
        print_message "前端: http://localhost:3000"
        print_message "后端: http://localhost:5000"
    else
        print_error "docker-compose.ubuntu18.yml 文件不存在"
    fi
}

# 停止服务
stop_services() {
    print_step "停止服务"
    if [ -f "docker-compose.ubuntu18.yml" ]; then
        docker-compose -f docker-compose.ubuntu18.yml down
        print_message "服务已停止"
    else
        print_error "docker-compose.ubuntu18.yml 文件不存在"
    fi
}

# 查看服务状态
check_services() {
    print_step "查看服务状态"
    if [ -f "docker-compose.ubuntu18.yml" ]; then
        echo
        print_message "=== Docker 容器状态 ==="
        docker-compose -f docker-compose.ubuntu18.yml ps
        echo
        print_message "=== Docker 镜像列表 ==="
        docker images | grep -E "(ai-qa|REPOSITORY)"
        echo
        print_message "=== 系统资源使用 ==="
        docker system df
    else
        print_error "docker-compose.ubuntu18.yml 文件不存在"
    fi
}

# 显示帮助
show_help() {
    cat << 'EOF'
🔧 AI-QA 平台快速构建工具

=== 使用方法 ===

1. 交互式菜单:
   ./quick-build.sh

2. 直接命令:
   ./quick-build.sh full        # 完整构建
   ./quick-build.sh continue    # 继续构建
   ./quick-build.sh status      # 查看状态
   ./quick-build.sh backend     # 重新构建后端
   ./quick-build.sh frontend    # 重新构建前端
   ./quick-build.sh start       # 启动服务
   ./quick-build.sh stop        # 停止服务
   ./quick-build.sh clean       # 清理重建

=== 故障排除 ===

1. 构建中断:
   - 使用 "继续构建" 选项
   - 或运行: ./quick-build.sh continue

2. 镜像构建失败:
   - 检查网络代理设置
   - 重新下载基础镜像
   - 清理后重新构建

3. 服务启动失败:
   - 检查端口占用: netstat -tlnp | grep :3000
   - 查看容器日志: docker-compose logs -f

4. 代理问题:
   - 确保设置了正确的 HTTP_PROXY
   - 检查 NO_PROXY 配置

=== 常用命令 ===

查看日志:
  docker-compose -f docker-compose.ubuntu18.yml logs -f

进入容器:
  docker-compose -f docker-compose.ubuntu18.yml exec backend bash
  docker-compose -f docker-compose.ubuntu18.yml exec frontend sh

清理无用镜像:
  docker system prune -f

EOF
}

# 主函数
main() {
    # 检查必要文件
    check_scripts
    
    # 解析命令行参数
    case "${1:-}" in
        full|build)
            full_build
            ;;
        continue|cont)
            continue_build
            ;;
        status|stat)
            show_status
            ;;
        backend|be)
            rebuild_backend
            ;;
        frontend|fe)
            rebuild_frontend
            ;;
        images|img)
            redownload_images
            ;;
        clean|reset)
            clean_rebuild
            ;;
        env|setup)
            setup_environment
            ;;
        start|up)
            start_services
            ;;
        stop|down)
            stop_services
            ;;
        check|ps)
            check_services
            ;;
        help|-h|--help)
            show_help
            ;;
        "")
            # 交互式菜单
            while true; do
                show_menu
                read choice
                case $choice in
                    1) full_build ;;
                    2) continue_build ;;
                    3) show_status ;;
                    4) rebuild_backend ;;
                    5) rebuild_frontend ;;
                    6) redownload_images ;;
                    7) clean_rebuild ;;
                    8) setup_environment ;;
                    9) start_services ;;
                    10) stop_services ;;
                    11) check_services ;;
                    12) show_help ;;
                    0) exit 0 ;;
                    *) print_error "无效选择，请输入 0-12" ;;
                esac
                echo
                echo -n "按Enter键继续..."
                read
            done
            ;;
        *)
            print_error "未知参数: $1"
            echo "使用 './quick-build.sh help' 查看帮助"
            exit 1
            ;;
    esac
}

# 脚本入口
main "$@"
