import logging

import httpx
import asyncio
import uvicorn
from typing import Dict, List, Optional
from collections import defaultdict
from models.base import Group, Backend, Proxy
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse

from utils.base import join_url, LOGGER


def get_current_backend(group: Group, row: int) -> Optional[str]:
    if 0 <= row < len(group.backends):
        return group.backends[row].url
    return None


class ProxyServer:
    def __init__(self, proxys: List[Proxy]):
        self.servers: Dict[int, List[Group]] = { proxy.port: proxy.groups for proxy in proxys }
        self.apps = {}  # 存储每个端口对应的FastAPI实例
        
        # 为每个端口创建FastAPI实例
        for port in self.servers.keys():
            self.create_server(port)

    def create_server(self, port: int):
        app = FastAPI()
        app.middleware("http")(self.proxy_middleware)
        config = uvicorn.Config(app, host="0.0.0.0", port=port)
        server = uvicorn.Server(config)
        self.apps[port] = server
        return server

    async def start_servers(self):
        """启动所有端口的服务器"""
        tasks = []
        for port, server in self.apps.items():
            task = asyncio.create_task(server.serve())
            tasks.append(task)
        
        # 使用asyncio同时启动所有服务器
        await asyncio.gather(*tasks)

    def restart_server(self):
        """重启代理服务器"""
        stop_servers = [] # 将要停止的服务器
        new_servers = [] # 将要新启动的服务器
        
        # 找出需要停止的服务器（在self.apps中存在但在self.servers中不存在的端口）
        for port in self.apps.keys():
            if port not in self.servers:
                stop_servers.append(port)
        
        # 找出需要新启动的服务器（在self.servers中存在但在self.apps中不存在的端口）
        for port in self.servers.keys():
            if port not in self.apps:
                # 创建新的FastAPI实例
                self.create_server(port)
                new_servers.append(port)
        
        # 停止需要停止的服务器
        for port in stop_servers:
            asyncio.create_task(self.stop_server(port))
        
        # 启动新的服务器
        for port in new_servers:
            server = self.create_server(port)
            asyncio.create_task(server.serve())

    async def stop_server(self, port: int):
        """关闭指定端口的服务器"""
        if port in self.apps:
            server = self.apps[port]
            # 关闭所有连接
            await server.shutdown()
            # 从字典中移除
            del self.apps[port]
            LOGGER.info(f"停止端口 {port} 的服务器")

    async def proxy_middleware(self, request: Request, call_next):
        # 获取当前端口对应的组
        port = request.url.port
        groups = self.servers.get(port, [])
        
        # 获取请求路径
        path = request.url.path
        
        # 查找匹配的组
        target_group = None
        for group in groups:
            if path.startswith(group.path):
                target_group = group
                break

        try:
            port = int(target_group.current_backend)
        except:
            return JSONResponse(content={"error": '无可用或未启用后端服务'}, status_code=503)

        url = get_current_backend(target_group, port)
        if not target_group or not url:
            return await call_next(request)
            
        # 构建目标URL
        target_path = path[len(target_group.path):]  # 移除组路径前缀
        target_url = join_url(url, target_path)
        
        # 转发请求
        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=dict(request.headers),
                    params=dict(request.query_params),
                    content=await request.body()
                )
                
                return StreamingResponse(
                    response.iter_bytes(),
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
            except ConnectionError as e:
                return JSONResponse(content={"error": '目标服务器未运行或不可用'}, status_code=503)
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

    async def select_healthy_backend(self, group: Group):
        """选择一个健康的后端服务"""
        for idx, backend in enumerate(group.backends):
            if await self.check_backend_health(backend.url):
                group.current_backend = idx
                return True
        return False

    @classmethod
    async def check_backend_health(cls, url: str) -> bool:
        """检查后端健康状态"""     
        try:
            async with httpx.AsyncClient() as client:
                await client.get(url, timeout=2.0)
                return True
        except:
            return False
