#!/bin/bash

# 端口配置应用脚本
# 根据端口检查结果自动修改Docker Compose配置

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

# 检查配置文件
check_config_files() {
    print_step "检查配置文件..."
    
    if [ ! -f ".port-config" ]; then
        print_error "端口配置文件 .port-config 不存在"
        print_message "请先运行: ./check-ports.sh"
        exit 1
    fi
    
    if [ ! -f "docker-compose.ubuntu18.yml" ]; then
        print_error "Docker Compose配置文件不存在"
        exit 1
    fi
    
    print_message "✅ 配置文件检查通过"
}

# 加载端口配置
load_port_config() {
    print_step "加载端口配置..."
    
    source .port-config
    
    print_message "加载的端口配置："
    echo "├── 前端HTTP: $FRONTEND_HTTP_PORT"
    echo "├── 前端HTTPS: $FRONTEND_HTTPS_PORT"
    echo "├── 后端API: $BACKEND_API_PORT"
    echo "├── Redis: $REDIS_PORT"
    echo "└── Prometheus: $PROMETHEUS_PORT"
}

# 备份原配置
backup_original_config() {
    print_step "备份原配置文件..."
    
    timestamp=$(date +%Y%m%d_%H%M%S)
    cp docker-compose.ubuntu18.yml "docker-compose.ubuntu18.yml.backup_$timestamp"
    
    print_message "✅ 原配置已备份为: docker-compose.ubuntu18.yml.backup_$timestamp"
}

# 应用端口配置
apply_port_configuration() {
    print_step "应用新端口配置..."
    
    # 创建临时文件
    temp_file=$(mktemp)
    
    # 使用sed替换端口配置
    sed "s/\"80:80\"/\"$DOCKER_FRONTEND_HTTP\"/g" docker-compose.ubuntu18.yml > "$temp_file"
    sed -i "s/\"443:443\"/\"$DOCKER_FRONTEND_HTTPS\"/g" "$temp_file"
    sed -i "s/\"8088:8088\"/\"$DOCKER_BACKEND_API\"/g" "$temp_file"
    sed -i "s/\"6379:6379\"/\"$DOCKER_REDIS\"/g" "$temp_file"
    sed -i "s/\"9090:9090\"/\"$DOCKER_PROMETHEUS\"/g" "$temp_file"
    
    # 替换原文件
    mv "$temp_file" docker-compose.ubuntu18.yml
    
    print_message "✅ 端口配置已应用到 docker-compose.ubuntu18.yml"
}

# 更新环境变量文件
update_env_file() {
    print_step "更新环境变量文件..."
    
    if [ -f ".env" ]; then
        # 添加端口配置到.env文件
        if ! grep -q "# Port Configuration" .env; then
            cat >> .env << EOF

# Port Configuration
FRONTEND_HTTP_PORT=$FRONTEND_HTTP_PORT
FRONTEND_HTTPS_PORT=$FRONTEND_HTTPS_PORT
BACKEND_API_PORT=$BACKEND_API_PORT
REDIS_PORT=$REDIS_PORT
PROMETHEUS_PORT=$PROMETHEUS_PORT
EOF
            print_message "✅ 端口配置已添加到 .env 文件"
        else
            print_message "✅ .env 文件中已存在端口配置"
        fi
    else
        print_warning ".env 文件不存在，跳过环境变量更新"
    fi
}

# 更新快速部署脚本
update_deployment_script() {
    print_step "更新部署脚本中的端口引用..."
    
    if [ -f "quick-deploy-with-proxy.sh" ]; then
        # 创建临时文件
        temp_file=$(mktemp)
        
        # 更新脚本中的端口引用
        sed "s/localhost:8088/localhost:$BACKEND_API_PORT/g" quick-deploy-with-proxy.sh > "$temp_file"
        sed -i "s/localhost:80/localhost:$FRONTEND_HTTP_PORT/g" "$temp_file"
        sed -i "s/localhost/localhost:$FRONTEND_HTTP_PORT/g" "$temp_file"
        
        mv "$temp_file" quick-deploy-with-proxy.sh
        chmod +x quick-deploy-with-proxy.sh
        
        print_message "✅ 部署脚本端口引用已更新"
    fi
}

# 生成访问信息
generate_access_info() {
    print_step "生成访问信息..."
    
    # 获取服务器IP
    SERVER_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "YOUR_SERVER_IP")
    
    cat > access-info.txt << EOF
# 智能问答系统访问信息
# 生成时间: $(date)

## 服务访问地址
前端页面:     http://$SERVER_IP:$FRONTEND_HTTP_PORT
前端HTTPS:    https://$SERVER_IP:$FRONTEND_HTTPS_PORT
后端API:      http://$SERVER_IP:$BACKEND_API_PORT
Redis缓存:    $SERVER_IP:$REDIS_PORT
监控面板:     http://$SERVER_IP:$PROMETHEUS_PORT

## API测试命令
# 健康检查
curl http://$SERVER_IP:$BACKEND_API_PORT/api/health

# 前端健康检查
curl http://$SERVER_IP:$FRONTEND_HTTP_PORT/health

## Docker命令
# 查看容器状态
docker-compose -f docker-compose.ubuntu18.yml ps

# 查看日志
docker-compose -f docker-compose.ubuntu18.yml logs

# 重启服务
docker-compose -f docker-compose.ubuntu18.yml restart

## 防火墙配置 (如果需要)
sudo ufw allow $FRONTEND_HTTP_PORT
sudo ufw allow $FRONTEND_HTTPS_PORT
sudo ufw allow $BACKEND_API_PORT
sudo ufw allow $REDIS_PORT
sudo ufw allow $PROMETHEUS_PORT

## 默认登录信息
用户名: admin
密码: admin123
EOF
    
    print_message "✅ 访问信息已生成: access-info.txt"
}

# 验证配置
verify_configuration() {
    print_step "验证配置文件..."
    
    # 检查Docker Compose文件语法
    if docker-compose -f docker-compose.ubuntu18.yml config > /dev/null 2>&1; then
        print_message "✅ Docker Compose配置文件语法正确"
    else
        print_error "❌ Docker Compose配置文件语法错误"
        print_message "正在恢复备份..."
        
        # 恢复最新备份
        latest_backup=$(ls -t docker-compose.ubuntu18.yml.backup_* 2>/dev/null | head -1)
        if [ -n "$latest_backup" ]; then
            cp "$latest_backup" docker-compose.ubuntu18.yml
            print_message "已恢复备份: $latest_backup"
        fi
        exit 1
    fi
    
    # 显示修改后的端口配置
    print_message "修改后的端口配置："
    grep -E "^\s*-\s*\"[0-9]+:[0-9]+\"" docker-compose.ubuntu18.yml | sed 's/^[ \t]*/  /'
}

# 显示下一步操作
show_next_steps() {
    print_header "端口配置完成！"
    
    echo "✅ 端口配置已成功应用"
    echo
    echo "下一步操作："
    echo
    echo "1. 查看访问信息："
    echo "   cat access-info.txt"
    echo
    echo "2. 重新部署服务："
    echo "   docker-compose -f docker-compose.ubuntu18.yml down"
    echo "   docker-compose -f docker-compose.ubuntu18.yml up -d --build"
    echo
    echo "3. 或使用快速部署脚本："
    echo "   ./quick-deploy-with-proxy.sh"
    echo
    echo "4. 配置防火墙（如果需要）："
    echo "   sudo ufw allow $FRONTEND_HTTP_PORT"
    echo "   sudo ufw allow $BACKEND_API_PORT"
    echo
    echo "5. 访问系统："
    echo "   前端: http://$(hostname -I | awk '{print $1}'):$FRONTEND_HTTP_PORT"
    echo "   后端: http://$(hostname -I | awk '{print $1}'):$BACKEND_API_PORT"
    echo
}

# 主函数
main() {
    print_message "端口配置应用脚本 v1.0"
    print_message "========================="
    
    check_config_files
    load_port_config
    backup_original_config
    apply_port_configuration
    update_env_file
    update_deployment_script
    generate_access_info
    verify_configuration
    show_next_steps
    
    print_message "✅ 端口配置应用完成！"
}

# 错误处理
trap 'print_error "脚本执行过程中发生错误"; exit 1' ERR

# 运行主函数
main "$@"
