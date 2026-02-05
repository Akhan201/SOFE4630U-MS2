import json
import time
import mysql.connector
from google.cloud import pubsub_v1

PROJECT_ID = "project-ccd0306c-1455-4582-930"
SUBSCRIPTION_NAME = "MS2Design-sub"

MYSQL_HOST = "34.130.8.87"
MYSQL_USER = "usr"
MYSQL_PASSWORD = "sofe4630u"
MYSQL_DB = "Readings"
TABLE = "DesignMS2"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_NAME)

print(f"Pulling messages from {subscription_path} -> storing into {MYSQL_DB}.{TABLE}")

def to_float_or_none(x):
    if x is None or x == "":
        return None
    try:
        return float(x)
    except ValueError:
        return None

def to_int_time_or_none(x):
    # time in your JSON is like "1768708698.49" but DB expects BIGINT
    if x is None or x == "":
        return None
    try:
        return int(float(x))
    except ValueError:
        return None

def insert_row(record):
    # Create a NEW DB connection per insert (avoids thread/connection issues)
    db = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        connection_timeout=10,
        autocommit=True,
    )
    cur = db.cursor()

    t = to_int_time_or_none(record.get("time"))
    profile = record.get("profileName")  # string
    temp = to_float_or_none(record.get("temperature"))
    hum = to_float_or_none(record.get("humidity"))
    pres = to_float_or_none(record.get("pressure"))

    sql = f"""
        INSERT INTO {TABLE} (time, profile_name, temperature, humidity, pressure)
        VALUES (%s, %s, %s, %s, %s)
    """
    cur.execute(sql, (t, profile, temp, hum, pres))

    cur.close()
    db.close()

while True:
    response = subscriber.pull(
        request={"subscription": subscription_path, "max_messages": 10},
        timeout=20,
    )

    if not response.received_messages:
        continue

    ack_ids = []
    for rm in response.received_messages:
        msg = rm.message
        try:
            record = json.loads(msg.data.decode("utf-8"))
            insert_row(record)
            print("Inserted:", record)
            ack_ids.append(rm.ack_id)
        except Exception as e:
            print("Failed:", msg.data, "| error:", e)
            # Don't ack -> Pub/Sub will retry later

    if ack_ids:
        subscriber.acknowledge(request={"subscription": subscription_path, "ack_ids": ack_ids})

    time.sleep(0.2)



