import httpx
import asyncio
from proxy.base import ProxyServer
from utils.base import ConfigManager


async def check_backend_health(url: str) -> bool:
    """检查后端健康状态"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=2.0)
            is_healthy = response.status_code == 200
            return is_healthy
    except:
        return False


async def start_server():
    proxy = ProxyServer(ConfigManager.get_config())
    await proxy.start_servers()


if __name__ == '__main__':
    # asyncio.run(check_backend_health("http://localhost:3011"))
    asyncio.run(start_server())
