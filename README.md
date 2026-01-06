# 🌍 Edge Monitor - 分布式多云服务器监控系统

![Build Status](https://img.shields.io/github/actions/workflow/status/pilliaredrw/edge_monitor/deploy.yml?label=CI%2FCD&style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi)
![Vue3](https://img.shields.io/badge/Frontend-Vue.js_3-4FC08D?style=flat-square&logo=vue.js)
![Docker](https://img.shields.io/badge/Deployment-Docker-2496ED?style=flat-square&logo=docker)

> 一个轻量级服务器监控系统（PULL）。支持多节点并发采集、配置热重载与全链路自动化部署。

## 📖 项目简介

Edge Monitor 旨在解决多云环境（Multi-Cloud）下的服务器状态统一监控问题。区别于传统的重量级监控方案（如 Prometheus + Grafana），本项目专注于**极简部署**与**毫秒级响应**。

系统采用 **Agent-Aggregator** 架构，前端使用 Vue3 构建实时大屏，后端基于 FastAPI 的异步并发能力处理全球节点的聚合查询。

## 🚀 核心特性 (Key Features)

- **⚡ 高并发异步采集**：利用 Python `asyncio` + `httpx` 实现对全球节点的非阻塞并发请求，有效解决跨国网络高延迟问题。
- **🔄 GitOps 自动化运维**：深度集成 GitHub Actions。代码提交即触发前端编译、后端 Docker 构建、跨服务器传输及服务热重启。
- **🔥 配置热重载 (Hot-Reload)**：通过 Docker Volume 挂载与文件系统监听，无需重启容器即可动态增减监控节点。
- **🛡️ 生产级安全实践**：采用配置与机密分离策略（Config/Secret Separation），Token 通过 CI/CD 环境变量注入，Cloudflare 提供全站 HTTPS 保护。
- **🐳 全链路容器化**：Agent 端与 Dashboard 端均采用 Docker 部署，确保环境一致性。

## 🛠️ 技术栈 (Tech Stack)

### Backend (Aggregator & Agent)
- **Framework**: FastAPI (Python 3.11)
- **Concurrency**: Python Asyncio, httpx
- **System Info**: Psutil
- **Architecture**: RESTful API

### Frontend (Dashboard)
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Network**: Axios

### DevOps & Infrastructure
- **CI/CD**: GitHub Actions (Build, SCP, SSH, Docker Ops)
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (Reverse Proxy)
- **Security**: Cloudflare (Flexible SSL), Token-based Auth

## 🏗️ 系统架构

```mermaid
graph LR
    User[User / Browser] -->|HTTPS| CF[Cloudflare]
    CF -->|HTTP| Nginx[Aliyun Nginx]
    
    subgraph "Cloud Server (Dashboard)"
        Nginx -->|Static Files| Vue[Vue Frontend /var/www]
        Nginx -->|Proxy /api| Agg[Aggregator Container :9000]
        Config[config.yaml] -.->|Volume Mount| Agg
    end
    
    subgraph "Global Edge Nodes"
        Agg -->|Async HTTP Check| Agent1[🇩🇪 Node Agent]
        Agg -->|Async HTTP Check| Agent2[🇺🇸 Node Agent]
        Agg -->|Async HTTP Check| Agent3[🇭🇰 Node Agent]
    end
