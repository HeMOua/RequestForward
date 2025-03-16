import { BaseModel } from './base'
import { ipcMain } from 'electron'
import { Logger } from 'winston'
import { handleRequest } from '../utils/request'

export class ServiceModel extends BaseModel {
  async create(data: CreateServiceDto): Promise<number> {
    const sql = `
      INSERT INTO services (
        name, address, port, 
        group_id, comment
      ) VALUES (?, ?, ?, ?, ?)
    `
    const params = [data.name, data.address, data.port, data.groupId, data.comment]
    return this.run(sql, params)
  }

  async findAll(): Promise<Service[]> {
    return this.all<Service>('SELECT * FROM services')
  }

  async findById(id: number): Promise<Service | undefined> {
    return this.get<Service>('SELECT * FROM services WHERE id = ?', [id])
  }

  async findByGroupId(groupId: number): Promise<Service[]> {
    return this.all<Service>('SELECT * FROM services WHERE group_id = ?', [groupId])
  }

  async update(id: number, data: Partial<CreateServiceDto>): Promise<number> {
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
      UPDATE services 
      SET ${fields.join(', ')}, update_time = CURRENT_TIMESTAMP 
      WHERE id = ?
    `

    return this.run(sql, values)
  }

  async delete(id: number): Promise<number> {
    return this.run('DELETE FROM services WHERE id = ?', [id])
  }
}

export const initServiceApi = (db: Database, logger: Logger) => {
  const model = new ServiceModel(db.getDatabase())

  ipcMain.handle('service:create', async (_, data: CreateServiceDto) => {
    return handleRequest(() => model.create(data), logger, 'Create service')
  })

  ipcMain.handle('service:findAll', async () => {
    return handleRequest(() => model.findAll(), logger, 'Find all services')
  })

  ipcMain.handle('service:findById', async (_, id: number) => {
    return handleRequest(() => model.findById(id), logger, `Find service by id ${id}`)
  })

  ipcMain.handle('service:findByGroupId', async (_, groupId: number) => {
    return handleRequest(
      () => model.findByGroupId(groupId),
      logger,
      `Find services by group id ${groupId}`
    )
  })

  ipcMain.handle('service:update', async (_, id: number, data: Partial<CreateServiceDto>) => {
    return handleRequest(() => model.update(id, data), logger, `Update service with id ${id}`)
  })

  ipcMain.handle('service:delete', async (_, id: number) => {
    return handleRequest(() => model.delete(id), logger, `Delete service with id ${id}`)
  })

  return model
}
