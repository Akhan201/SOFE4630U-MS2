import time
import mysql.connector 

# Authentication setup
#files = glob("my-first-project231-*.json") 
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = files[0]

# MySQL configuration
MYSQL_HOST = "34.130.8.87"  
MYSQL_USER = "usr"
MYSQL_PASSWORD = "sofe4630u"
MYSQL_DB = "Readings"
TABLE = "DesignMS2"

# Initialize MySQL connection
db = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DB,
)
cur = db.cursor(dictionary=True)

# Polling loop to read new rows from the database
last_seen_id = 0
print("Polling MySQL for new rows... ")

# Polling loop to read new rows from the database
try:
    while True:
        cur.execute(
            f"SELECT * FROM {TABLE} WHERE id > %s ORDER BY id ASC LIMIT 50", 
            (last_seen_id,)
        )
        rows = cur.fetchall()

        for row in rows:
            print(row)
            last_seen_id = max(last_seen_id, row["ID"])

        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    cur.close()
    db.close()
