import time
import csv
import json
from google.cloud import pubsub_v1

# Authentication setup
#files = glob("my-first-project231-*.json")
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = files[0]

#Project and topic configuration
PROJECT_ID = "project-ccd0306c-1455-4582-930"
TOPIC_NAME = "MS2Design"  
CSV_FILE_PATH = "Labels.csv"

# Initialize Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)
print(f"Publishing messages to {topic_path}")

while True:
# Read CSV and publish messages
    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

    # Iterate through each row in the CSV
        for row in reader:
            print("ROW:", row)
            record_dict = dict(row) # Convert OrderedDict to regular dict

            #Convert dict to JSON string and then to bytes
            message_bytes = json.dumps(record_dict).encode("utf-8")

            # Publish the message
            try:
                future = publisher.publish(topic_path, message_bytes)
                print("Published (queued):",record_dict) 
                print("Message ID:", future.result())


            except Exception as e:
                print(f"Failed to publish {record_dict}: {e}")

            time.sleep(1)  # small delay so you can see messages flowing
