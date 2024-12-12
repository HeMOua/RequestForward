import httpx
import asyncio
import uvicorn
from typing import Dict, List
from collections import defaultdict
from models.base import Group, Backend, Proxy
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse


class ProxyServer:
    def __init__(self, proxys: List[Proxy]):
        self.proxys = proxys
        self.servers = { proxy.port: proxy.groups for proxy in proxys }
        self.apps = {}  # 存储每个端口对应的FastAPI实例
        
        # 为每个端口创建FastAPI实例
        for port in self.servers.keys():
            app = FastAPI()
            app.middleware("http")(self.proxy_middleware)
            self.apps[port] = app
        
        # 启动所有服务器
        self.start_servers()

    def start_servers(self):
        """启动所有端口的服务器"""
        configs = []
        for port, app in self.apps.items():
            config = uvicorn.Config(app, host="0.0.0.0", port=port)
            configs.append(config)
        
        # 使用asyncio同时启动所有服务器
        servers = [uvicorn.Server(config) for config in configs]
        asyncio.run(self._start_servers(servers))

    async def _start_servers(self, servers):
        """异步启动所有服务器"""
        await asyncio.gather(*(server.serve() for server in servers))

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
        
        if not target_group or not target_group.current_backend:
            return await call_next(request)
            
        # 构建目标URL
        target_path = path[len(target_group.path):]  # 移除组路径前缀
        target_url = f"{target_group.current_backend}{target_path}"
        
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
            except Exception as e:
                return JSONResponse(content={"error": str(e)}, status_code=500)

    async def select_healthy_backend(self, group: Group):
        """选择一个健康的后端服务"""
        for backend in group.backends:
            if await self.check_backend_health(backend, group.health_check_path):
                self.group_backends[group.path] = backend
                return True
        return False

    async def check_backend_health(self, backend: Backend, health_check_path: str) -> bool:
        """检查后端健康状态"""
        if self.backend_health[backend.url]:
            return True
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{backend.url}{health_check_path}", timeout=5.0)
                is_healthy = response.status_code == 200
                self.backend_health[backend.url] = is_healthy
                return is_healthy
        except:
            self.backend_health[backend.url] = False
            return False
