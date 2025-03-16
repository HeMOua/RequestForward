interface BaseEntity {
  id: number
  createTime: string
  updateTime: string
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
  refreshInterval: number
}

interface CreateGroupDto {
  name: string
  alias?: string
  address: string
  port: number
  status: number
  refresh?: boolean
  refreshInterval?: number
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
  groupId: number
  comment?: string
}

interface UpdateServiceDto extends Partial<CreateServiceDto> {}
