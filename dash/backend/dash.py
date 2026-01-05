import os
import yaml
import httpx
import asyncio
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from dotenv import load_dotenv

# 1. 初始化：加载环境变量与日志配置
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 全局变量：用于配置文件热重载缓存
CONFIG_FILE = "config.yaml"
_cached_config = None
_last_mtime = 0

def load_env_placeholders(cfg):
    """将配置中的 ${AGENT_TOKEN} 占位符替换为真实环境变量"""
    placeholder = "${AGENT_TOKEN}"
    if cfg.get('global', {}).get('auth_token') == placeholder:
        env_val = os.getenv("AGENT_TOKEN")
        if env_val:
            cfg['global']['auth_token'] = env_val
            logger.info("AGENT_TOKEN 注入成功")
        else:
            logger.warning("未找到 AGENT_TOKEN 环境变量，请检查 .env 或系统设置")
    return cfg

def get_config():
    """读取配置文件，仅在文件修改时间变更时重新加载（热重载）"""
    global _cached_config, _last_mtime
    try:
        current_mtime = os.path.getmtime(CONFIG_FILE)
        if current_mtime > _last_mtime:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                raw_cfg = yaml.safe_load(f)
                _cached_config = load_env_placeholders(raw_cfg)
                _last_mtime = current_mtime
                logger.info("检测到配置变更，已完成热重载")
        return _cached_config
    except Exception as e:
        logger.error(f"配置加载失败: {e}")
        return _cached_config

# 2. FastAPI 应用与跨域配置
app = FastAPI(title="Edge Monitor Dashboard")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. 核心逻辑：异步拉取单个节点状态
async def fetch_node_status(client: httpx.AsyncClient, node: Dict[str, Any], global_cfg: Dict):
    node_id = node['id']
    node_url = node['url'].rstrip('/')
    
    # 优先使用节点独有的 token，否则使用全局 token
    timeout = global_cfg['global'].get('timeout', 5)
    token = node.get('token', global_cfg['global'].get('auth_token'))
    
    offline_data = {
        "node_id": node_id, 
        "node_name": node['name'], 
        "status": "offline",
        "cpu": {"cpu_usage_percent": 0},
        "memory": {"usage_percent": 0, "available_gb": 0, "total_gb": 0}
    }

    try:
        resp = await client.get(
            f"{node_url}/system/status", 
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout
        )
        if resp.status_code == 200:
            data = resp.json()
            data.update({"node_id": node_id, "node_name": node['name'], "status": "online"})
            return data
        return {**offline_data, "error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {**offline_data, "error": "Connection Failed"}

# 4. API 路由
@app.get("/api/nodes")
async def get_node_list():
    """返回简单的节点 ID 和名称清单，供前端渲染骨架"""
    cfg = get_config()
    return [{"id": n["id"], "name": n["name"]} for n in cfg.get('nodes', [])]

@app.get("/api/node/{node_id}/status")
async def get_single_node_status(node_id: str):
    """为前端提供单个节点的实时状态查询"""
    cfg = get_config()
    node = next((n for n in cfg['nodes'] if n['id'] == node_id), None)
    
    if not node:
        return {"error": "Node not found", "status": "offline"}

    async with httpx.AsyncClient() as client:
        return await fetch_node_status(client, node, cfg)

if __name__ == "__main__":
    import uvicorn
    # 监听 0.0.0.0 以允许外部/Docker 访问
    uvicorn.run(app, host="0.0.0.0", port=9000)