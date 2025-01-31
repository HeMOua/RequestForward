import { Logger } from 'winston'
import { initDatabase } from './models/database'
import { appConfig } from './config'
import { initGroupApi } from './models/group'
import { initServiceApi } from './models/service'

export const initAppFunction = async (logger: Logger) => {
  // 初始化数据库
  const db = await initDatabase(appConfig.dbPath)

  // 初始化 Group 接口
  initGroupApi(db, logger)

  // 初始化 Service 接口
  initServiceApi(db, logger)
}
