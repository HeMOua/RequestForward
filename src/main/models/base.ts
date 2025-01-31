import { Database } from 'sqlite3'

export class BaseModel {
  constructor(protected db: Database) {}

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
        else resolve(row as T)
      })
    })
  }

  protected async all<T>(sql: string, params: any[] = []): Promise<T[]> {
    return new Promise((resolve, reject) => {
      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err)
        else resolve(rows as T[])
      })
    })
  }
}
