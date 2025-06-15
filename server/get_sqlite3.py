import sqlite3

# Connect to the SQLite database
connection = sqlite3.connect('main.db')
cursor = connection.cursor()

# Query to get data from the last 7 days
cursor.execute("""SELECT * FROM realtime_data 
WHERE id IN (
    SELECT MIN(id) 
    FROM realtime_data 
    GROUP BY strftime('%Y-%m-%d %H:%M', timestamp)
)
AND timestamp >= datetime('now', '-1 minutes');""")

# Fetch all results
results = cursor.fetchall()

# Display the results
for row in results:
    print(row)

# Close the connection
connection.close()