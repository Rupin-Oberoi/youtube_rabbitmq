import argparse
import os
import pika
import sys
import time
import json
import threading

IP_ADDR = 'localhost'

class UploadRequest:
    def __init__(self, youtuber, video_title, datetime):
        self.youtuber = youtuber
        self.video_title = video_title
        self.datetime = datetime

def publishVideo(youtuber, videoName):
    connection = pika.BlockingConnection(pika.ConnectionParameters(IP_ADDR))
    channel = connection.channel()
    channel.queue_declare(queue = 'youtuber_upload_request')
    vid = UploadRequest(youtuber, videoName, time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
    m1 = json.dumps(vid.__dict__)
    channel.basic_publish(exchange='', routing_key='youtuber_upload_request', body=m1)
    
    

def main():
    args = sys.argv
    
    if len(args) < 3:
        print("Usage: youtuber.py <youtuber_name> <video_name>")
        sys.exit(1)
        
    youtuber_name = args[1]
    video_name = " ".join(args[2:])
    publishVideo(youtuber_name, video_name)
    
if __name__ == '__main__':
    main()
