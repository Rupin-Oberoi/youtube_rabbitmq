import pika
import sys
import threading
import time
import json

def updateSubscription(mode, youtuber, username):
    
    def subscription_response_callback(frame):
        if frame.method.NAME == 'Basic.Ack':
            print('SUCCESS') 
            
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue = 'q_subscription_request')
    m1 = json.dumps({'user': username, 'youtuber': youtuber, 'subscribe': True if mode == 's' else False})
    # channel.confirm_delivery()
    # channel.add_on_return_callback(subscription_response_callback)
    channel.basic_publish(exchange='', routing_key='q_subscription_request', body=m1)
    
    
    q = channel.queue_declare(queue = f'q_sub_notif_{username}', exclusive=False, durable=True)
    q_name = q.method.queue
    channel.exchange_declare(exchange = 'ex_subscription_notifications', exchange_type='direct', durable = True)
    if mode == 's':
        channel.queue_bind(queue=q_name, exchange = 'ex_subscription_notifications', routing_key = youtuber)
    elif mode == 'u':
        channel.queue_unbind(queue = q_name, exchange='ex_subscription_notifications', routing_key = youtuber)
    
    connection.close()

def receiveNotifications(username):
    def callback(ch, method, properties, body):
        m1 = json.loads(body)
        print(f"New video from {m1['youtuber']}: {m1['video_title']}")
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
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
    
    if len(args) == 2:
        username = args[1]
        print(f'Hello {username}!')
        print(f'Here are the latest videos from your subscriptions:')
        subscriptions = set()
        receiveNotifications(username)
        
    elif len(args) == 4:
        username = args[1]
        mode = args[2]
        if not(mode) in ['s', 'u']:
            raise ValueError('Invalid option: use s for subscribe and u for unsubscribe')
        youtuber = args[3]
        
        updateSubscription(mode, youtuber, username)
        
        time.sleep(1)
        print(f'Hello {username}!')
        print(f'Here are the latest videos from your subscriptions:')
        receiveNotifications(username)
        
    else:
        print("Usage: user.py <username> or user.py <username> <mode> <youtuber>")
        sys.exit(1)