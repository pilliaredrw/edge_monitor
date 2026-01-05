from tokenize import Token
from fastapi import FastAPI, HTTPException, Depends
from fastapi import security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time 
import os
import agent.monitor_core as monitor_core 

# 创建 API 实例，初始化一个 Web 服务对象
app = FastAPI(title="探针")

security_scheme = HTTPBearer()
# 定义验证方法

# API_TOKEN = "test_token"
API_TOKEN = os.getenv("AGENT_TOKEN")
# 获取环境变量中的 Token 值

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing token")
    return credentials.credentials

@app.get("/")
def root():
    return {"status": "running", "message": "Edge Monitor is active"}
    # 在根目录显示服务启动

@app.get("/system/status", dependencies=[Depends(verify_token)])
def get_system_status():
    """
    获取系统核心资源数据
    """
    # 1. 调用核心
    cpu = monitor_core.get_cpu_info()
    mem = monitor_core.get_memory_info()
    # 2. 拼装成 JSON 格式返回
    # FastAPI 会自动把这个字典转换成 JSON 字符串
    return {
        "timestamp": int(time.time()), # 时间戳
        "cpu": cpu,
        "memory": mem
    }