import { Database } from 'sqlite3'

export class BaseModel {
  constructor(protected db: Database) {}

  // camelCase -> snake_case
  protected camelToSnake(obj: any): any {
    const newObj: any = {}
    for (const key in obj) {
      const snakeKey = key.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)
      newObj[snakeKey] = obj[key]
    }
    return newObj
  }

  // snake_case -> camelCase
  protected snakeToCamel<T>(obj: any): T {
    if (!obj) return obj
    const newObj: any = {}
    for (const key in obj) {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
      newObj[camelKey] = obj[key]
    }
    return newObj as T
  }

  protected async run(sql: string, params: any[] = []): Promise<number> {
    return new Promise((resolve, reject) => {
      this.db.run(sql, params, function (err) {
        if (err) reject(err)
        else resolve(this.lastID)
      })
    })
  }

  protected async get<T>(sql: string, params: any[] = []): Promise<T | undefined> {
    return new Promise((resolve, reject) => {
      this.db.get(sql, params, (err, row) => {
        if (err) reject(err)
        else resolve(this.snakeToCamel<T>(row))
      })
    })
  }

  protected async all<T>(sql: string, params: any[] = []): Promise<T[]> {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err)
        else resolve(rows.map((row) => this.snakeToCamel<T>(row)))
      })
    })
  }
}
