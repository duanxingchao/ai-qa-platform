#!/bin/bash
# 自动化部署配置文件
# 请根据实际环境修改以下配置

# ===========================================
# 代理配置
# ===========================================
HTTP_PROXY="http://proxysysx.his.hihonor.com:8080"
HTTPS_PROXY="http://proxysysx.his.hihonor.com:8080"
FTP_PROXY="http://proxysysx.his.hihonor.com:8080"
NO_PROXY="localhost,127.0.0.1,w3.hihonor.com,mgit-tm.ipd.hihonor.com,mirrors.chinatelecom.hihonor.io"
PROXY_AUTH_REQUIRED="n"  # y/n
PROXY_USERNAME=""        # 如果需要认证
PROXY_PASSWORD=""        # 如果需要认证

# ===========================================
# 数据库配置  
# ===========================================
DB_HOST="dws-digital-datalake.digital.hihonor.com"
DB_PORT="8000"
DB_NAME="需要在运行时输入"
DB_USER="dmp_rnd_xa"
DB_PASSWORD="需要在运行时输入"

# ===========================================
# API配置
# ===========================================
USE_GLORY_API="y"        # y/n 是否使用荣耀生产API

# ===========================================
# 高级配置（一般不需要修改）
# ===========================================
FRONTEND_PORT="18080"
BACKEND_PORT="8088"
REDIS_PORT="6379"

# 镜像源配置
USE_COMPANY_MIRROR="y"  # y/n 是否使用公司内部镜像源
USE_ALIYUN_MIRROR="n"   # y/n 是否使用阿里云镜像源（备用）

# ===========================================
# 配置验证函数
# ===========================================
validate_config() {
    local errors=0
    
    if [[ -z "$HTTP_PROXY" ]]; then
        echo "❌ 请配置 HTTP_PROXY"
        errors=$((errors + 1))
    fi
    
    if [[ -z "$HTTPS_PROXY" ]]; then
        echo "❌ 请配置 HTTPS_PROXY"
        errors=$((errors + 1))
    fi
    
    if [[ -z "$DB_HOST" || "$DB_HOST" == "您的数据库主机地址" ]]; then
        echo "❌ 请配置 DB_HOST"
        errors=$((errors + 1))
    fi
    
    if [[ -z "$DB_NAME" || "$DB_NAME" == "需要在运行时输入" ]]; then
        echo "⚠️  DB_NAME 需要在运行时输入"
    fi
    
    if [[ -z "$DB_PASSWORD" || "$DB_PASSWORD" == "需要在运行时输入" ]]; then
        echo "⚠️  DB_PASSWORD 需要在运行时输入"
    fi
    
    if [[ $errors -gt 0 ]]; then
        echo ""
        echo "请编辑 deploy-config.sh 文件，填入正确的配置信息"
        echo "编辑命令: nano deploy-config.sh"
        exit 1
    fi
    
    echo "✅ 配置验证通过"
}

# 导出环境变量
export_config() {
    export HTTP_PROXY
    export HTTPS_PROXY
    export FTP_PROXY
    export NO_PROXY
    export PROXY_AUTH_REQUIRED
    export PROXY_USERNAME  
    export PROXY_PASSWORD
    export DB_HOST
    export DB_PORT
    export DB_NAME
    export DB_USER
    export DB_PASSWORD
    export USE_GLORY_API
    export USE_COMPANY_MIRROR
    export USE_ALIYUN_MIRROR
    export FRONTEND_PORT
    export BACKEND_PORT
    export REDIS_PORT
    
    # 设置系统代理环境变量
    export http_proxy="$HTTP_PROXY"
    export https_proxy="$HTTPS_PROXY"
    export ftp_proxy="$FTP_PROXY"
    export no_proxy="$NO_PROXY"
}
