import yaml
import httpx
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

# 1. 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 2. 加载配置
def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()
GLOBAL_TIMEOUT = config['global']['timeout']
DEFAULT_TOKEN = config['global']['auth_token']

app = FastAPI(title="Edge Monitor Dashboard")

# 3. 解决 CORS 跨域问题
# 允许你的 Vue 前端 (通常跑在 localhost:5173) 访问这个接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def fetch_node_status(client: httpx.AsyncClient, node: Dict[str, Any]):
    """
    异步拉取单个节点，包含详细的错误处理
    """
    node_id = node['id']
    node_name = node['name']
    node_url = node['url'].rstrip('/')
    # 如果节点没配 token，就用全局 token
    token = node.get('token', DEFAULT_TOKEN)
    
    target_url = f"{node_url}/system/status"
    
    # 默认离线结构
    offline_data = {
        "node_id": node_id,
        "node_name": node_name,
        "status": "offline", # 前端根据这个字段变红
        "error": "Unknown",
        "cpu": {"cpu_usage_percent": 0},
        "memory": {"usage_percent": 0, "available_gb": 0, "total_gb": 0}
    }

    try:
        # 发起异步请求
        resp = await client.get(
            target_url, 
            headers={"Authorization": f"Bearer {token}"},
            timeout=GLOBAL_TIMEOUT
        )
        
        if resp.status_code == 200:
            data = resp.json()
            # 注入元数据，方便前端展示
            data['node_id'] = node_id
            data['node_name'] = node_name
            data['status'] = 'online' # 前端根据这个字段变绿
            return data
            
        elif resp.status_code == 401 or resp.status_code == 403:
            logger.warning(f"Node {node_name} Auth Failed")
            offline_data['error'] = "Auth Failed"
            return offline_data
            
        else:
            logger.error(f"Node {node_name} HTTP {resp.status_code}")
            offline_data['error'] = f"HTTP {resp.status_code}"
            return offline_data

    except httpx.ConnectTimeout:
        logger.warning(f"Node {node_name} Timeout ({GLOBAL_TIMEOUT}s)")
        offline_data['error'] = "Timeout"
        return offline_data
        
    except httpx.ConnectError:
        logger.warning(f"Node {node_name} Unreachable")
        offline_data['error'] = "Unreachable"
        return offline_data
        
    except Exception as e:
        logger.error(f"Node {node_name} Error: {str(e)}")
        offline_data['error'] = "System Error"
        return offline_data

@app.get("/api/dashboard")
async def dashboard_endpoint():
    """
    聚合接口：一次性并发拉取所有节点
    """
    nodes = config['nodes']
    
    # 使用 httpx 的异步上下文管理器
    # 这比每次请求都创建一个 client 要快得多（复用 TCP 连接）
    async with httpx.AsyncClient() as client:
        # 创建任务列表
        tasks = [fetch_node_status(client, node) for node in nodes]
        
        # 并发执行！
        # 哪怕德国机器要 4秒，内网机器只要 0.1秒
        # 整个接口返回的总时间 = 最慢的那个请求的时间 (约 4秒)，而不是所有时间之和
        results = await asyncio.gather(*tasks)
        
    return results

if __name__ == "__main__":
    # 生产环境监听 0.0.0.0，允许从外部访问聚合器
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)