import sqlite3 from 'sqlite3'

export class Database {
  private db: sqlite3.Database

  constructor(dbPath: string) {
    this.db = new sqlite3.Database(dbPath)
  }

  async init(): Promise<void> {
    const groups = `
      CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        alias TEXT NOT NULL,
        address TEXT NOT NULL,
        port INTEGER NOT NULL,
        status INTEGER DEFAULT 0,
        refresh INTEGER DEFAULT 0,
        refresh_interval INTEGER DEFAULT 300,
        comment TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `

    const services = `
      CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        port INTEGER NOT NULL,
        group_id INTEGER NOT NULL,
        comment TEXT,
        create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (group_id) REFERENCES groups (id)
      )
    `

    return new Promise((resolve, reject) => {
      this.db.serialize(() => {
        this.db.run(groups).run(services, (err) => {
          if (err) reject(err)
          else resolve()
        })
      })
    })
  }

  getDatabase(): sqlite3.Database {
    return this.db
  }

  async close(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.close((err) => {
        if (err) reject(err)
        else resolve()
      })
    })
  }
}

export const initDatabase = async (dbPath: string) => {
  const db = new Database(dbPath)
  return db.init().then(() => db)
}
