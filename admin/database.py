import sqlite3


def create_database():

    connection = sqlite3.connect("logs.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        ip TEXT,
        website TEXT,
        category TEXT,
        decision TEXT,
        server TEXT
    )
    """)

    connection.commit()
    connection.close()


def save_log(time, ip, website, category, decision, server):

    connection = sqlite3.connect("logs.db")
    cursor = connection.cursor()

    cursor.execute("""
    INSERT INTO logs(time, ip, website, category, decision, server)
    VALUES(?,?,?,?,?,?)
    """, (time, ip, website, category, decision, server))

    connection.commit()
    connection.close()


create_database()


def get_logs():

    connection = sqlite3.connect("logs.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY id DESC")

    logs = cursor.fetchall()

    connection.close()

    return logs
def get_statistics():

    connection = sqlite3.connect("logs.db")
    cursor = connection.cursor()

    # Total Requests
    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]

    # Allowed Requests
    cursor.execute("SELECT COUNT(*) FROM logs WHERE decision='Allowed'")
    allowed = cursor.fetchone()[0]

    # Blocked Requests
    cursor.execute("SELECT COUNT(*) FROM logs WHERE decision='Blocked'")
    blocked = cursor.fetchone()[0]

    # Connected Clients (Unique IPs)
    cursor.execute("SELECT COUNT(DISTINCT ip) FROM logs")
    clients = cursor.fetchone()[0]

    connection.close()

    return total, allowed, blocked, clients