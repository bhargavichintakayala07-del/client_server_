import sqlite3


connection = sqlite3.connect("logs.db")

cursor = connection.cursor()


cursor.execute("""
INSERT INTO logs
(time, client_ip, website, category, decision, server)

VALUES
(
'10:30',
'192.168.1.10',
'github.com',
'Educational',
'Allowed',
'Server1'
)
""")


connection.commit()

connection.close()


print("Log Added")