import sqlite3
from pprint import pprint

# Step 1: Connect to the SQLite database (creates the database if it doesn't exist)
connection = sqlite3.connect('main.db')

# Step 2: Create a cursor object to interact with the database
cursor = connection.cursor()

# Step 3: Create a table (if it doesn't already exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS realtime_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    voltage REAL,
    A1 REAL,
    A2 REAL,
    A3 REAL,
    A4 REAL,
    A5 REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')


voltage = 220.5
A1 = 5.2
A2 = 4.8
A3 = 5.0
A4 = 4.9
A5 = 5.1

# Step 4: Insert data into the table
cursor.execute('''
INSERT INTO realtime_data (voltage, A1, A2, A3, A4, A5)
VALUES (?, ?, ?, ?, ?, ?)
''', (voltage, A1, A2, A3, A4, A5))

# Step 5: Commit the changes to save them to the database
connection.commit()

# Step 6: Fetch and display the data (just to confirm the insert)
cursor.execute("SELECT * FROM realtime_data")
pprint(cursor.fetchall())  # It will print the rows in the table

# Step 7: Close the connection
connection.close()
