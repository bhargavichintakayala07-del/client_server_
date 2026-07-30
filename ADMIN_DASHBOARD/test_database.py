import sqlite3

connection = sqlite3.connect("logs.db")
cursor = connection.cursor()

# Column name fixed from 'client_ip' to 'ip'
cursor.execute("""
INSERT INTO logs
(time, ip, website, category, decision, server)
VALUES
(
'10:30 PM',
'192.168.137.5',
'github.com',
'Educational',
'ALLOWED',
'Hotspot Gateway Node'
)
""")

connection.commit()
connection.close()

print("✅ Test Log Inserted Successfully into Database!")