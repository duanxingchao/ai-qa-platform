"""
Flask应用启动文件
"""
import os
from dotenv import load_dotenv
from app import create_app

# 加载环境变量
load_dotenv()

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    # 开发模式运行
    port = int(os.environ.get('PORT', 8088))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    ) 