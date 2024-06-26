import pika
import sys
import time
import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

IP_ADDRESS = os.environ.get('ip_address')
credentials = pika.PlainCredentials(os.environ.get('username'), os.environ.get('password'))

def updateSubscription(mode, youtuber, username):
    
    # def subscription_response_callback(frame):
    #     if frame.method.NAME == 'Basic.Ack':
    #         print('SUCCESS') 
            
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = IP_ADDRESS, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue = 'q_subscription_request')
    m1 = json.dumps({'user': username, 'youtuber': youtuber, 'subscribe': True if mode == 's' else False})
    # channel.confirm_delivery()
    channel.basic_publish(exchange='', routing_key='q_subscription_request', body=m1)
    if youtuber is None:
        return
    print('SUCCESS')
    
    
    q = channel.queue_declare(queue = f'q_sub_notif_{username}', exclusive=False, durable=True)
    q_name = q.method.queue
    channel.exchange_declare(exchange = 'ex_subscription_notifications', exchange_type='direct', durable = True)
    if mode == 's':
        channel.queue_bind(queue=q_name, exchange = 'ex_subscription_notifications', routing_key = youtuber)
    elif mode == 'u':
        channel.queue_unbind(queue = q_name, exchange='ex_subscription_notifications', routing_key = youtuber)
    
    connection.close()

def receiveNotifications(username, justUnsubbedFrom = None):
    def callback(ch, method, properties, body):
        m1 = json.loads(body)
        if justUnsubbedFrom and m1['youtuber'] == justUnsubbedFrom:
            return
        print(f"New Notification: {m1['youtuber']} uploaded {m1['video_title']}")
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host = IP_ADDRESS, credentials=credentials))
    channel = connection.channel()
    channel.exchange_declare(exchange='ex_subscription_notifications', exchange_type='direct', durable = True)
    # if isnewuser:
    #     q = channel.queue_declare(queue=username, exclusive=False, durable = True)
    # since it doesn't matter if a queue with same name already exists
    q = channel.queue_declare(queue=f'q_sub_notif_{username}', exclusive = False, durable = True)
    q_name = q.method.queue
    # for youtuber in youtubers:
    #     channel.queue_bind(exchange='subscription_notifications', queue=q_name, routing_key=youtuber)
    
    channel.basic_consume(queue=q_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()
    

if __name__ == '__main__':
    args = sys.argv
    try:
        if len(args) == 2:
            username = args[1]
            #print(f'Hello {username}!')
            #print(f'Here are the latest videos from your subscriptions:')
            subscriptions = set()
            updateSubscription(None, None, username)
            receiveNotifications(username)
            
        elif len(args) == 4:
            username = args[1]
            mode = args[2]
            if not(mode) in ['s', 'u']:
                raise ValueError('Invalid option: use s for subscribe and u for unsubscribe')
            youtuber = args[3]
            
            updateSubscription(mode, youtuber, username)
            
            time.sleep(1)
            #print(f'Hello {username}!')
            #print(f'Here are the latest videos from your subscriptions:')
            if mode == 's':
                receiveNotifications(username)
            elif mode == 'u':
                receiveNotifications(username, youtuber)
            
        else:
            print("Valid Usage: user.py <username> or user.py <username> <mode> <youtuber>")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)