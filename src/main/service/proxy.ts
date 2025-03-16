import { createProxyMiddleware } from 'http-proxy-middleware'
import { Application } from 'express'
import { EventEmitter } from 'events'
import { Logger } from 'winston'

interface ActiveProxy {
  group: Group
  service: Service
  middleware: any
}

export class ProxyService extends EventEmitter {
  private activeProxies: Map<number, ActiveProxy> = new Map()
  private app: Application
  private checkIntervals: Map<number, NodeJS.Timeout> = new Map()
  private logger: Logger

  constructor(app: Application, logger: Logger) {
    super()
    this.app = app
    this.logger = logger
  }

  // 启动组的转发服务
  async startGroup(group: Group, service: Service): Promise<void> {
    // 如果已经有活跃的代理，先停止它
    if (this.activeProxies.has(group.id)) {
      await this.stopGroup(group.id)
    }

    const proxyConfig = {
      target: `http://${service.address}:${service.port}`,
      changeOrigin: true,
      ws: true, // 支持 websocket
      pathRewrite: {
        [`^/proxy/${group.id}`]: '', // 移除代理路径前缀
        [`^/proxy/${group.alias}`]: '' // 移除代理路径前缀
      },
      onProxyReq: (proxyReq: any, req: any, res: any) => {
        // 可以在这里修改请求头
        proxyReq.setHeader('X-Proxy-Group', group.id)
      },
      onError: (err: Error, req: any, res: any) => {
        this.logger.error(`Proxy error for group ${group.id}:`, err)
        res.writeHead(500, {
          'Content-Type': 'application/json'
        })
        res.end(JSON.stringify({ error: 'Proxy error occurred' }))
      }
    }

    const middleware = createProxyMiddleware(proxyConfig)

    // 注册代理中间件
    this.app.use(`/proxy/${group.id}`, middleware)
    this.app.use(`/proxy/${group.alias}`, middleware)

    this.activeProxies.set(group.id, {
      group,
      service,
      middleware
    })

    // 如果配置了自动刷新，启动健康检查
    if (group.refresh && group.refreshInterval > 0) {
      this.startHealthCheck(group)
    }
  }

  // 停止组的转发服务
  async stopGroup(groupId: number): Promise<void> {
    const proxy = this.activeProxies.get(groupId)
    if (!proxy) {
      throw new Error(`No active proxy found for group ${groupId}`)
    }

    // 停止健康检查
    this.stopHealthCheck(groupId)

    // 移除代理中间件
    const router = this.app._router
    const middlewareIndex = router.stack.findIndex(
      (layer: any) => layer.handle === proxy.middleware
    )

    if (middlewareIndex !== -1) {
      router.stack.splice(middlewareIndex, 1)
    }

    this.activeProxies.delete(groupId)
  }

  // 启动所有组的转发服务
  async startAll(groups: Group[], servicesByGroup: Map<number, Service[]>): Promise<void> {
    for (const group of groups) {
      if (group.status === 1) {
        const services = servicesByGroup.get(group.id) || []
        if (services.length > 0) {
          // 选择第一个服务作为活跃服务
          await this.startGroup(group, services[0])
        }
      }
    }
  }

  // 停止所有组的转发服务
  async stopAll(): Promise<void> {
    for (const groupId of this.activeProxies.keys()) {
      await this.stopGroup(groupId)
    }
  }

  // 切换组的活跃服务
  async switchService(groupId: number, service: Service): Promise<void> {
    const proxy = this.activeProxies.get(groupId)
    if (!proxy) {
      throw new Error(`No active proxy found for group ${groupId}`)
    }

    await this.startGroup(proxy.group, service)
  }

  // 检查服务是否可用
  async checkService(service: Service): Promise<boolean> {
    try {
      const response = await fetch(`http://${service.address}:${service.port}`)
      return response.ok
    } catch (error) {
      return false
    }
  }

  // 启动健康检查
  private startHealthCheck(group: Group): void {
    if (this.checkIntervals.has(group.id)) {
      return
    }

    const interval = setInterval(async () => {
      const proxy = this.activeProxies.get(group.id)
      if (!proxy) return

      const isAlive = await this.checkService(proxy.service)

      this.emit('healthCheck', {
        groupId: group.id,
        serviceId: proxy.service.id,
        status: isAlive ? 'healthy' : 'unhealthy',
        message: isAlive ? 'Service is healthy' : 'Service is unhealthy'
      })

      if (!isAlive) {
        this.emit('serviceDown', {
          groupId: group.id,
          serviceId: proxy.service.id
        })
      }
    }, group.refreshInterval * 1000)

    this.checkIntervals.set(group.id, interval)
  }

  // 停止健康检查
  private stopHealthCheck(groupId: number): void {
    const interval = this.checkIntervals.get(groupId)
    if (interval) {
      clearInterval(interval)
      this.checkIntervals.delete(groupId)
    }
  }

  // 获取组的当前活跃服务
  getActiveService(groupId: number): Service | null {
    const proxy = this.activeProxies.get(groupId)
    return proxy ? proxy.service : null
  }

  // 判断组是否正在运行
  isGroupRunning(groupId: number): boolean {
    return this.activeProxies.has(groupId)
  }
}
