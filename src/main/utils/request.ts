import { Logger } from 'winston'

// 通用的错误处理函数
export async function handleRequest<T>(
  operation: () => Promise<T>,
  logger: Logger,
  context: string
): Promise<ApiResponse<T>> {
  try {
    const result = await operation()
    logger.debug(`${context} success: ${JSON.stringify(result)}`)
    return { success: true, data: result }
  } catch (error: any) {
    logger.error(`${context} failed: ${JSON.stringify(error)}`)
    return { success: false, error: error.message }
  }
}
