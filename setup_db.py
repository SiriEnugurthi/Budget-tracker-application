import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS Users (
    uid INTEGER PRIMARY KEY AUTOINCREMENT,
    u_name TEXT NOT NULL,
    u_pass TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Budget (
    bid INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER,
    budget DECIMAL(10,2),
    savings_goal DECIMAL(10,2),
    FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE SET NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Categories (
    cid INTEGER PRIMARY KEY AUTOINCREMENT,
    c_name TEXT,
    c_type TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS Transactions (
    tid INTEGER PRIMARY KEY AUTOINCREMENT,
    uid INTEGER,
    cid INTEGER,
    t_name TEXT,
    t_amount DECIMAL(10,2),
    description TEXT,
    date TEXT,
    type TEXT,
    is_recurring INTEGER DEFAULT 0,
    FOREIGN KEY (uid) REFERENCES Users(uid) ON DELETE CASCADE,
    FOREIGN KEY (cid) REFERENCES Categories(cid) ON DELETE SET NULL
)
''')

conn.commit()
conn.close()

print("Database created successfully.")