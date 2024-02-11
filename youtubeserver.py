import os
import pika
import sys
import threading
import time
import json

youtubers = []

class UploadRequest:
    def __init__(self, youtuber, video_title, datetime):
        self.youtuber = youtuber
        self.video_title = video_title
        self.datetime = datetime

def consume_user_requests():
    def callback(ch, method, properties, body):
        pass

def consume_youtuber_requests():
    def callback(ch, method, properties, body):
        message = UploadRequest(**json.loads(body))
        print(f"Youtuber {message.youtuber} has uploaded a new video titled {message.video_title} at {message.datetime}")
        global youtubers
        if message.youtuber not in youtubers:
            youtubers.append(body)
        
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    ch = connection.channel()
    ch.queue_declare(queue='youtuber_upload_request')
    ch.basic_consume(queue='youtuber_upload_request', on_message_callback=callback, auto_ack=True)
    ch.start_consuming()

def notify_users():
    pass

def main():
    t1 = threading.Thread(target=consume_youtuber_requests)
    t1.daemon = True
    t1.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    
    
if __name__ == '__main__':
    main()