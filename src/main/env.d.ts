interface BaseEntity {
  id: number
  create_time: string
  update_time: string
  comment?: string
}

interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

interface Database {
  init: () => Promise<void>
  getDatabase: () => sqlite3.Database
  close: () => Promise<void>
}

interface Group extends BaseEntity {
  name: string
  alias: string
  address: string
  port: number
  status: number
  refresh: boolean
  refresh_interval: number
}

interface CreateGroupDto {
  name: string
  alias?: string
  address: string
  port: number
  status: number
  refresh?: boolean
  refresh_interval?: number
  comment?: string
}

interface Service extends BaseEntity {
  name: string
  address: string
  port: number
  group_id: number
}

interface CreateServiceDto {
  name: string
  address: string
  port: number
  group_id: number
  comment?: string
}

interface UpdateServiceDto extends Partial<CreateServiceDto> {}
