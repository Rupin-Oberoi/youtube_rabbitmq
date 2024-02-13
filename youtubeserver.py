import os
import pika
import sys
import threading
import time
import json

youtubers = []
users = []
subscriptions = {}

class UploadRequest:
    def __init__(self, youtuber, video_title, datetime):
        self.youtuber = youtuber
        self.video_title = video_title
        self.datetime = datetime

def consume_user_requests():
    def callback(ch, method, properties, body):
        m1 = json.loads(body)
        if m1['subscribe']:
            subscriptions[m1['youtuber']].add(m1['user'])
            print(f"User {m1['user']} has subscribed to {m1['youtuber']}")
            # ch.queue_declare(queue='subscription_request_response')
            # ch.basic_publish(exchange='', routing_key='subscription_request_response', body='SUCCESS')
        else:
            subscriptions[m1['youtuber']].remove(m1['user'])
            print(f"User {m1['user']} has unsubscribed from {m1['youtuber']}")
            # ch.queue_declare(queue='subscription_request_response')
            # ch.basic_publish(exchange='', routing_key='subscription_request_response', body='SUCCESS')
        
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    ch = connection.channel()
    ch.queue_declare(queue='q_subscription_request')
    ch.basic_consume(queue='q_subscription_request', on_message_callback=callback, auto_ack=True)
    ch.start_consuming()

def consume_youtuber_requests():
    def callback(ch, method, properties, body):
        message = UploadRequest(**json.loads(body))
        print(f"Youtuber {message.youtuber} has uploaded a new video titled {message.video_title} at {message.datetime}")
        global youtubers
        if message.youtuber not in youtubers:
            youtubers.append(body)
            subscriptions[message.youtuber] = set()
        notify_users(message.youtuber, message.video_title)
        
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    ch = connection.channel()
    ch.queue_declare(queue='youtuber_upload_request')
    ch.basic_consume(queue='youtuber_upload_request', on_message_callback=callback, auto_ack=True)
    ch.start_consuming()

def notify_users(youtuber, video_title):
    global subscriptions
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    ch = connection.channel()
    # sub_queue = ch.queue_declare(queue='', exclusive=True)
    ch.exchange_declare(exchange='ex_subscription_notifications', exchange_type='direct', durable = True)
    # ch.queue_bind(exchange='subscription_notifications', queue=sub_queue.method.queue)
    ch.basic_publish(exchange='ex_subscription_notifications', routing_key=youtuber, body=json.dumps({'youtuber': youtuber, 'video_title': video_title}),
                     properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))
    connection.close()
    

def main():
    t1 = threading.Thread(target=consume_youtuber_requests)
    t1.daemon = True
    t1.start()
    
    time.sleep(1)
    
    t2 = threading.Thread(target=consume_user_requests)
    t2.daemon = True
    t2.start()
    
    # t3 = threading.Thread(target = notify_users)
    # t3.daemon = True
    # t3.start()
    
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