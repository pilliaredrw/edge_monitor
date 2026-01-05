import psutil
import time

def get_memory_info():
    # 读取 /proc/meminfo 模拟  'free' 命令
    # virtual_memory() 返回一个对象，包含了内存的各种状态
    mem = psutil.virtual_memory()
    # 转换为GB
    total_gb = mem.total / (1024 ** 3)
    available_gb = mem.available / (1024 ** 3)

    # mem.percent 实际上就是 (total - available) / total 的计算结果
    return { 
        "total_gb": round(total_gb, 2),
        "available_gb": round(available_gb, 2),
        "usage_percent": mem.percent
    }

def get_cpu_info():
    # 读取 /proc/stat 模拟 Linux 'top' 命令中的 CPU 负载
    cpu_usage = psutil.cpu_percent(interval=1) # interval=1 阻塞程序1秒钟，计算这1秒内 CPU 时间片的变化
    # 获取 CPU 核心数，对应 /proc/cpuinfo
    cpu_count = psutil.cpu_count(logical=True)
    
    return {
        "cpu_usage_percent": cpu_usage,
        "cpu_cores": cpu_count
    }

def printInfo(mem_info, cpu_info):
    print(f"[内存] 总量: {mem_info['total_gb']} GB, 可用: {mem_info['available_gb']} GB, 使用率: {mem_info['usage_percent']}%")
    print(f"[CPU] 核心数: {cpu_info['cpu_cores']}, 当前负载: {cpu_info['cpu_usage_percent']}%")

# test
if __name__ == "__main__":
    print("=== 开始采集系统数据 ===")

    mem_data = get_memory_info()
    cpu_data = get_cpu_info()
    printInfo(mem_data, cpu_data)
