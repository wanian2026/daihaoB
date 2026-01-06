"""
FastAPI 主启动文件
"""
import sys
import os

# 设置工作空间路径（用于静态文件服务）
os.environ['COZE_WORKSPACE_PATH'] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 使用真实数据模式（禁用Mock交易所）
os.environ['USE_MOCK_EXCHANGE'] = 'false'

from web.api import app

if __name__ == "__main__":
    import uvicorn
    # 使用 8080 端口避免 9000 端口的 API 网关冲突
    uvicorn.run(app, host="0.0.0.0", port=8080)
