import { BaseModel } from './base'
import { ipcMain } from 'electron'
import { Logger } from 'winston'
import { handleRequest } from '../utils/request'

export class GroupModel extends BaseModel {
  async create(data: CreateGroupDto): Promise<number> {
    const sql = `
      INSERT INTO groups (
        name, alias, address, port, refresh, 
        refresh_interval, comment, create_time
      ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    `
    const params = [
      data.name,
      data.address,
      data.port,
      data.refresh ?? false,
      data.refreshInterval ?? 300,
      data.comment
    ]
    return this.run(sql, params)
  }

  async findAll(): Promise<Group[]> {
    return this.all<Group>('SELECT * FROM groups')
  }

  async findById(id: number): Promise<Group | undefined> {
    return this.get<Group>('SELECT * FROM groups WHERE id = ?', [id])
  }

  async update(id: number, data: Partial<CreateGroupDto>): Promise<number> {
    const dbData = this.camelToSnake(data)

    const fields: string[] = []
    const values: any[] = []

    for (const [key, value] of Object.entries(dbData)) {
      if (value !== undefined) {
        fields.push(`${key} = ?`)
        values.push(value)
      }
    }

    if (fields.length === 0) return 0

    values.push(id)
    const sql = `
      UPDATE groups 
      SET ${fields.join(', ')}, update_time = CURRENT_TIMESTAMP 
      WHERE id = ?
    `

    return this.run(sql, values)
  }

  async delete(id: number): Promise<number> {
    return this.run('DELETE FROM groups WHERE id = ?', [id])
  }
}

export const initGroupApi = (db: Database, logger: Logger) => {
  const model = new GroupModel(db.getDatabase())

  ipcMain.handle('group:create', async (_, data: CreateGroupDto) => {
    return handleRequest(() => model.create(data), logger, 'Create group')
  })

  ipcMain.handle('group:findAll', async () => {
    return handleRequest(() => model.findAll(), logger, 'Find all groups')
  })

  ipcMain.handle('group:findById', async (_, id: number) => {
    return handleRequest(() => model.findById(id), logger, `Find group by id ${id}`)
  })

  ipcMain.handle('group:update', async (_, id: number, data: Partial<CreateGroupDto>) => {
    return handleRequest(() => model.update(id, data), logger, `Update group with id ${id}`)
  })

  ipcMain.handle('group:delete', async (_, id: number) => {
    return handleRequest(() => model.delete(id), logger, `Delete group with id ${id}`)
  })

  return model
}
