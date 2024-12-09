from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
from models import Group, Backend
from typing import Dict, Optional
import asyncio
from collections import defaultdict

class ProxyServer:
    def __init__(self):
        self.app = FastAPI()
        # 存储组及其当前活跃后端的映射
        self.group_backends: Dict[str, Backend] = {}
        # 存储所有组信息
        self.groups: Dict[int, Group] = {}
        # 后端健康状态
        self.backend_health: Dict[str, bool] = defaultdict(bool)
        
        # 注册路由
        self.app.middleware("http")(self.proxy_middleware)

    async def update_group_backends(self):
        for group in self.groups.values():
            await self.select_healthy_backend(group)

    async def proxy_middleware(self, request: Request, call_next):
        # 获取请求路径
        path = request.url.path
        
        # 查找匹配的组
        target_group = None
        for group in self.groups.values():
            if path.startswith(group.path):
                target_group = group
                break
        
        if not target_group:
            return await call_next(request)
            
        # 获取当前组的活跃后端
        if not target_group.current_backend:
            # 如果没有当前后端,选择第一个健康的后端作为当前后端
            return await call_next(request)

        # 构建目标URL
        target_path = path[len(target_group.path):]  # 移除组路径前缀
        target_url = f"{target_group.current_backend.url}{target_path}"
        
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
                # 当前后端出错,清空当前后端
                target_group.current_backend = None
                return {"error": str(e)}

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


proxy_server = ProxyServer()
app = proxy_server.app