import { Logger } from 'winston'

// 通用的错误处理函数
export async function handleRequest<T>(
  operation: () => Promise<T>,
  logger: Logger,
  context: string
) {
  try {
    const result = await operation()
    return { success: true, data: result }
  } catch (error: any) {
    logger.error(`${context} failed:`, error)
    return { success: false, error: error.message }
  }
}
