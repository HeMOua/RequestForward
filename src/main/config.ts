import { app } from 'electron'
import { join } from 'path'

export const appConfig = {
  appUserModelId: 'cn.jishuzhaix',
  logsPath: join(app.getPath('userData'), 'logs'),
  tempPath: join(app.getPath('userData'), 'temp'),
  dbPath: join(app.getPath('userData'), 'request-forwarder.db')
}

export const mainWindowConfig = {
  minWidth: 500,
  minHeight: 400
}
