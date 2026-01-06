"""
测试API路由
"""
import sys
import os

# 设置工作空间路径
os.environ['COZE_WORKSPACE_PATH'] = os.path.dirname(os.path.abspath(__file__))

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from web.api import app

def test_routes():
    """测试所有路由"""
    print("=" * 60)
    print("测试API路由")
    print("=" * 60)

    # 获取所有路由
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append({
                'path': route.path,
                'methods': list(route.methods),
                'name': getattr(route, 'name', None)
            })

    # 打印所有路由
    print(f"\n共找到 {len(routes)} 个路由:\n")

    # 分类路由
    main_routes = [r for r in routes if r['path'].startswith('/') and not r['path'].startswith('/api')]
    api_routes = [r for r in routes if r['path'].startswith('/api')]
    static_routes = [r for r in routes if r['path'].startswith('/static')]

    print("【主页路由】")
    for route in main_routes:
        methods = ', '.join(route['methods'])
        print(f"  {methods:10s} {route['path']}")
        if route['name']:
            print(f"             -> {route['name']}")

    print(f"\n【API路由】({len(api_routes)}个)")
    for route in api_routes:
        methods = ', '.join(route['methods'])
        print(f"  {methods:10s} {route['path']}")

    if static_routes:
        print(f"\n【静态文件】({len(static_routes)}个)")
        for route in static_routes:
            methods = ', '.join(route['methods'])
            print(f"  {methods:10s} {route['path']}")

    # 检查关键路由
    print("\n【关键路由检查】")
    has_root = any(r['path'] == '/' for r in routes)
    has_index = any(r['path'] == '/index.html' for r in routes)
    has_static = any(r['path'].startswith('/static') for r in routes)

    print(f"  / (主页): {'✅' if has_root else '❌'}")
    print(f"  /index.html: {'✅' if has_index else '❌'}")
    print(f"  /static: {'✅' if has_static else '❌'}")

    # 检查静态文件目录
    print("\n【静态文件目录检查】")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    web_dir = os.path.join(BASE_DIR, 'web')
    html_path = os.path.join(web_dir, 'index.html')

    print(f"  项目根目录: {BASE_DIR}")
    print(f"  Web目录: {web_dir}")
    print(f"  Web目录存在: {'✅' if os.path.exists(web_dir) else '❌'}")
    print(f"  index.html存在: {'✅' if os.path.exists(html_path) else '❌'}")

    if os.path.exists(html_path):
        with open(html_path, 'r') as f:
            content = f.read()
            print(f"  index.html大小: {len(content)} 字节")

if __name__ == '__main__':
    test_routes()
