#!/bin/bash

# 部署验证脚本
# 用于验证智能问答系统是否部署成功

set -e

echo "🔍 开始验证部署状态..."

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

print_step() {
    echo -e "${BLUE}[验证]${NC} $1"
}

# 验证计数器
TOTAL_CHECKS=0
PASSED_CHECKS=0

check_result() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ $1 -eq 0 ]; then
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        print_success "$2"
    else
        print_error "$2"
    fi
}

# 1. 验证Docker环境
verify_docker() {
    print_step "验证Docker环境..."
    
    # 检查Docker是否安装
    if command -v docker &> /dev/null; then
        docker_version=$(docker --version)
        check_result 0 "Docker已安装: $docker_version"
    else
        check_result 1 "Docker未安装"
        return 1
    fi
    
    # 检查Docker Compose是否安装
    if command -v docker-compose &> /dev/null; then
        compose_version=$(docker-compose --version)
        check_result 0 "Docker Compose已安装: $compose_version"
    else
        check_result 1 "Docker Compose未安装"
        return 1
    fi
    
    # 检查Docker服务状态
    if systemctl is-active --quiet docker; then
        check_result 0 "Docker服务正在运行"
    else
        check_result 1 "Docker服务未运行"
        return 1
    fi
    
    # 检查Docker权限
    if docker ps &> /dev/null; then
        check_result 0 "Docker权限正常"
    else
        check_result 1 "Docker权限不足"
        return 1
    fi
}

# 2. 验证项目文件
verify_project_files() {
    print_step "验证项目文件..."
    
    required_files=(
        "docker-compose.ubuntu18.yml"
        ".env"
        "backend/Dockerfile.ubuntu18"
        "frontend/Dockerfile.ubuntu18"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            check_result 0 "文件存在: $file"
        else
            check_result 1 "文件缺失: $file"
        fi
    done
}

# 3. 验证环境配置
verify_environment() {
    print_step "验证环境配置..."
    
    if [ -f ".env" ]; then
        check_result 0 ".env配置文件存在"
        
        # 检查关键配置项
        if grep -q "DATABASE_URL=postgresql://" .env; then
            if grep -q "用户名:密码@高斯数据库地址" .env; then
                check_result 1 "数据库配置未修改，请填入真实信息"
            else
                check_result 0 "数据库配置已设置"
            fi
        else
            check_result 1 "数据库配置缺失"
        fi
        
        if grep -q "SECRET_KEY=your-super-secret-key" .env; then
            check_result 1 "SECRET_KEY未修改，请设置安全密钥"
        else
            check_result 0 "SECRET_KEY已设置"
        fi
    else
        check_result 1 ".env配置文件不存在"
    fi
}

# 4. 验证容器状态
verify_containers() {
    print_step "验证容器状态..."
    
    # 检查容器是否运行
    if docker-compose -f docker-compose.ubuntu18.yml ps | grep -q "Up"; then
        check_result 0 "容器正在运行"
        
        # 检查各个服务
        services=("backend" "frontend" "redis")
        for service in "${services[@]}"; do
            if docker-compose -f docker-compose.ubuntu18.yml ps | grep "$service" | grep -q "Up"; then
                check_result 0 "$service 服务运行正常"
            else
                check_result 1 "$service 服务未运行"
            fi
        done
    else
        check_result 1 "没有容器在运行"
        print_warning "请先运行: docker-compose -f docker-compose.ubuntu18.yml up -d"
        return 1
    fi
}

# 5. 验证服务健康状态
verify_health() {
    print_step "验证服务健康状态..."
    
    # 等待服务启动
    print_info "等待服务完全启动..."
    sleep 10
    
    # 检查后端健康状态
    if curl -f -s http://localhost:8088/api/health > /dev/null; then
        check_result 0 "后端API健康检查通过"
    else
        check_result 1 "后端API健康检查失败"
    fi
    
    # 检查前端健康状态
    if curl -f -s http://localhost/health > /dev/null; then
        check_result 0 "前端服务健康检查通过"
    else
        check_result 1 "前端服务健康检查失败"
    fi
    
    # 检查Redis连接
    if docker-compose -f docker-compose.ubuntu18.yml exec -T redis redis-cli ping | grep -q PONG; then
        check_result 0 "Redis服务连接正常"
    else
        check_result 1 "Redis服务连接失败"
    fi
}

# 6. 验证数据库连接
verify_database() {
    print_step "验证数据库连接..."
    
    # 从.env文件读取数据库URL
    if [ -f ".env" ]; then
        db_url=$(grep "DATABASE_URL=" .env | cut -d'=' -f2)
        if [ -n "$db_url" ] && [[ "$db_url" != *"用户名:密码@高斯数据库地址"* ]]; then
            # 测试数据库连接
            if docker-compose -f docker-compose.ubuntu18.yml exec -T backend python -c "
from app import create_app
from app.utils.database import db
try:
    app = create_app()
    with app.app_context():
        result = db.engine.execute('SELECT 1').scalar()
        print('SUCCESS')
except Exception as e:
    print(f'ERROR: {e}')
" | grep -q "SUCCESS"; then
                check_result 0 "数据库连接测试成功"
            else
                check_result 1 "数据库连接测试失败"
            fi
        else
            check_result 1 "数据库配置未正确设置"
        fi
    else
        check_result 1 "无法读取数据库配置"
    fi
}

# 7. 验证网络访问
verify_network() {
    print_step "验证网络访问..."
    
    # 获取服务器IP
    server_ip=$(hostname -I | awk '{print $1}')
    print_info "服务器IP: $server_ip"
    
    # 检查端口是否开放
    ports=(80 8088)
    for port in "${ports[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            check_result 0 "端口 $port 已绑定"
        else
            check_result 1 "端口 $port 未绑定"
        fi
    done
    
    # 检查防火墙状态
    if command -v ufw &> /dev/null; then
        ufw_status=$(sudo ufw status | head -1)
        print_info "防火墙状态: $ufw_status"
        
        if [[ "$ufw_status" == *"active"* ]]; then
            print_warning "防火墙已启用，请确保开放了80和8088端口"
        fi
    fi
}

# 8. 验证功能完整性
verify_functionality() {
    print_step "验证功能完整性..."
    
    # 检查API端点
    api_endpoints=(
        "/api/health"
        "/api/questions"
        "/api/sync/status"
    )
    
    for endpoint in "${api_endpoints[@]}"; do
        if curl -f -s "http://localhost:8088$endpoint" > /dev/null; then
            check_result 0 "API端点可访问: $endpoint"
        else
            check_result 1 "API端点不可访问: $endpoint"
        fi
    done
    
    # 检查前端页面
    if curl -f -s http://localhost/ > /dev/null; then
        check_result 0 "前端页面可访问"
    else
        check_result 1 "前端页面不可访问"
    fi
}

# 生成验证报告
generate_report() {
    echo ""
    echo "📊 验证报告"
    echo "================================"
    echo "总检查项: $TOTAL_CHECKS"
    echo "通过检查: $PASSED_CHECKS"
    echo "失败检查: $((TOTAL_CHECKS - PASSED_CHECKS))"
    
    success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    echo "成功率: $success_rate%"
    
    echo ""
    if [ $success_rate -ge 90 ]; then
        print_success "🎉 部署验证成功！系统运行正常"
        echo ""
        echo "📋 访问信息："
        server_ip=$(hostname -I | awk '{print $1}')
        echo "  前端页面: http://$server_ip"
        echo "  后端API:  http://$server_ip:8088"
        echo "  默认账号: admin / admin123"
        echo ""
        echo "🔧 管理命令："
        echo "  查看日志: docker-compose -f docker-compose.ubuntu18.yml logs -f"
        echo "  重启服务: docker-compose -f docker-compose.ubuntu18.yml restart"
        echo "  停止服务: docker-compose -f docker-compose.ubuntu18.yml down"
    elif [ $success_rate -ge 70 ]; then
        print_warning "⚠️ 部署基本成功，但有部分问题需要解决"
        echo "请检查失败的项目并进行修复"
    else
        print_error "❌ 部署验证失败，需要重新部署"
        echo "请检查错误信息并重新执行部署步骤"
    fi
}

# 主函数
main() {
    echo "智能问答系统部署验证工具"
    echo "=========================="
    
    verify_docker
    verify_project_files
    verify_environment
    verify_containers
    verify_health
    verify_database
    verify_network
    verify_functionality
    generate_report
}

# 运行主函数
main "$@"
