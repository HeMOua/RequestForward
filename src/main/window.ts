import { join } from 'path'
import { Logger } from 'winston'
import { is } from '@electron-toolkit/utils'
import { shell, BrowserWindow } from 'electron'
import { mainWindowConfig } from './config'
import icon from '../../resources/icon.png?asset'

export function createWindow(store: Record<string, any>, logger: Logger): void {
  // 获取主窗口尺寸
  const mainWindowSize = store.get('main-window-size') as { width: number; height: number }

  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: mainWindowSize?.width ?? mainWindowConfig.minWidth,
    height: mainWindowSize?.height ?? mainWindowConfig.minHeight,
    minWidth: mainWindowConfig.minWidth,
    minHeight: mainWindowConfig.minHeight,
    show: false,
    autoHideMenuBar: true,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow.show()
    logger.info('Main window ready to show')
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url).then(() => {
      logger.info('Open external URL:', details.url)
    })
    return { action: 'deny' }
  })

  // 监听窗口获得焦点的事件
  mainWindow.on('focus', () => {
    mainWindow.webContents.send('main-window-focus')
  })

  // 监听窗口失去焦点的事件
  mainWindow.on('blur', () => {
    mainWindow.webContents.send('main-window-blur')
  })

  // 将窗口大小保存到 electron-store 中
  mainWindow.on('resize', () => {
    const { width, height } = mainWindow.getBounds()
    store.set('main-window-size', { width, height })
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL']).then(() => {
      logger.info('Main window loaded remote URL:', process.env['ELECTRON_RENDERER_URL'])
    })
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html')).then(() => {
      logger.info('Main window loaded local file:', join(__dirname, '../renderer/index.html'))
    })
  }
}
