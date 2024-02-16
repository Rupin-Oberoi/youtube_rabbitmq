import os
import pika
import sys
import time
import json
from dotenv import load_dotenv

load_dotenv(override=True)

IP_ADDRESS = os.environ.get('ip_address')
credentials = pika.PlainCredentials(os.environ.get('username'), os.environ.get('password'))

class UploadRequest:
    def __init__(self, youtuber, video_title, datetime):
        self.youtuber = youtuber
        self.video_title = video_title
        self.datetime = datetime

def publishVideo(youtuber, videoName):
    connection = pika.BlockingConnection(pika.ConnectionParameters(IP_ADDRESS, credentials=credentials))
    channel = connection.channel()
    # channel.confirm_delivery()
    channel.queue_declare(queue = 'q_youtuber_upload_request')
    vid = UploadRequest(youtuber, videoName, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    m1 = json.dumps(vid.__dict__)
    channel.basic_publish(exchange='', routing_key='q_youtuber_upload_request', body=m1)
    print('SUCCESS')
    

def main():
    args = sys.argv
    
    if len(args) < 3:
        print("Valid Usage: youtuber.py <youtuber_name> <video_name>")
        sys.exit(1)
        
    youtuber_name = args[1]
    video_name = " ".join(args[2:])
    publishVideo(youtuber_name, video_name)
    
if __name__ == '__main__':
    main()
