import sqlite3

def init_db():
    conn = sqlite3.connect('tictactoe.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scores (
            p1 TEXT, p2 TEXT, s1 INTEGER, s2 INTEGER,
            PRIMARY KEY (p1, p2)
        )''')
    conn.commit()
    conn.close()

def get_score(p1, p2):
    players = sorted([p1, p2])
    conn = sqlite3.connect('tictactoe.db')
    cursor = conn.cursor()
    cursor.execute("SELECT s1, s2 FROM scores WHERE p1=? AND p2=?", (players[0], players[1]))
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, 0)

def update_score(p1, p2, winner_name):
    players = sorted([p1, p2])
    s1, s2 = get_score(p1, p2)
    if winner_name == players[0]: s1 += 1
    elif winner_name == players[1]: s2 += 1
    conn = sqlite3.connect('tictactoe.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO scores VALUES (?, ?, ?, ?)", (players[0], players[1], s1, s2))
    conn.commit()
    conn.close()