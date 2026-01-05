import requests
import time
import os

# 1. 配置文件 (真实场景下应该读 YAML/JSON 文件)
# 假设你有两台机器：一台本地 Docker，一台(未来的)远程机器
NODES = [
    {
        "name": "Local-Docker",
        "url": "http://127.0.0.1:8080", # Docker 映射出的端口
        "token": "test_token"
    },
    # {
    #     "name": "Remote-Server-BJ",
    #     "url": "http://100.64.0.1:8000", 
    #     "token": "edge-secret-2025"
    # },
]

def fetch_status(node):
    """
    去拉取单台机器的数据
    """
    api_url = f"{node['url']}/system/status"
    headers = {"Authorization": f"Bearer {node['token']}"}
    
    try:
        # 设置 timeout 防止网络卡死导致整个面板卡住
        response = requests.get(api_url, headers=headers, timeout=2)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            return {"error": "Auth Failed"}
        else:
            return {"error": f"HTTP {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        return {"error": "Offline"}
    except Exception as e:
        return {"error": str(e)}

def clear_screen():
    # 兼容 Windows 和 Linux 的清屏
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("=== Edge Monitor Dashboard (Press Ctrl+C to stop) ===")
    
    while True:
        clear_screen()
        print(f"最后刷新时间: {time.strftime('%H:%M:%S')}\n")
        
        # 打印表头 (使用 f-string 对齐)
        print(f"{'节点名称':<15} | {'状态':<10} | {'CPU(%)':<8} | {'内存(GB)':<15}")
        print("-" * 60)
        
        for node in NODES:
            data = fetch_status(node)
            
            name = node['name']
            
            if "error" in data:
                print(f"{name:<15} | \033[31mDOWN\033[0m       | {'-':<8} | {data['error']:<15}")
            else:
                # 解析数据
                cpu = data['cpu']['cpu_usage_percent']
                mem_used = data['memory']['usage_percent']
                mem_total = data['memory']['total_gb']
                mem_avail = data['memory']['available_gb']
                
                # 简单的告警颜色逻辑
                status_color = "\033[32m" # 绿色
                if cpu > 80 or mem_used > 80:
                    status_color = "\033[31m" # 红色
                
                print(f"{name:<15} | {status_color}ONLINE\033[0m     | {cpu:<8} | {mem_avail}/{mem_total} (Free/Tot)")
        
        # 每 2 秒刷新一次
        time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n监控已停止")