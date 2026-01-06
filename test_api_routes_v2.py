"""
测试API路由 - 调试版本
"""
import sys
import os

# 设置工作空间路径
workspace = os.path.dirname(os.path.abspath(__file__))
print(f"设置 COZE_WORKSPACE_PATH = {workspace}")
os.environ['COZE_WORKSPACE_PATH'] = workspace

print(f"COZE_WORKSPACE_PATH = {os.getenv('COZE_WORKSPACE_PATH')}")

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(workspace, 'src'))

# 测试路径计算
test_file = os.path.join(workspace, 'src', 'web', 'api.py')
print(f"测试文件路径: {test_file}")
print(f"测试文件存在: {os.path.exists(test_file)}")

# 计算预期的BASE_DIR
expected_base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(test_file))))
print(f"预期BASE_DIR: {expected_base_dir}")

# 计算web目录
expected_web_dir = os.path.join(expected_base_dir, 'web')
print(f"预期web目录: {expected_web_dir}")
print(f"web目录存在: {os.path.exists(expected_web_dir)}")

# 计算index.html路径
expected_html_path = os.path.join(expected_web_dir, 'index.html')
print(f"预期index.html: {expected_html_path}")
print(f"index.html存在: {os.path.exists(expected_html_path)}")

print("\n现在导入web.api模块...")
from web.api import app, web_dir, BASE_DIR

print(f"\n导入后的值:")
print(f"BASE_DIR = {BASE_DIR}")
print(f"web_dir = {web_dir}")
print(f"web_dir存在: {os.path.exists(web_dir)}")

html_path = os.path.join(web_dir, 'index.html')
print(f"index.html路径: {html_path}")
print(f"index.html存在: {os.path.exists(html_path)}")
