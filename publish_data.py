import paho.mqtt.client as mqtt
import json
import datetime
import sys
import os
import time
import pickle
import threading

client_publish = None
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))


def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)


def control_command_publish():

    client_publish = mqtt.Client()
    client_publish.on_connect = on_connect
    client_publish.on_disconnect = on_disconnect
    client_publish.on_publish = on_publish
    client_publish.connect('20.194.104.191', 1883)
    topic_name = "/REQUEST/STREAMING/00000001-6077-cd85-8002-00000000192b"
    print(topic_name)
    command = {
            "NodeID":"00000001-6077-cd85-8002-00000000192b_0009",
            "Command":"ON",
            "RtspURL":"rtspt://admin:ygo1429@220.124.73.183/ch01/0",
            "BdNumber" : 10
        }
    client_publish.publish(topic_name, json.dumps(command), 1)
    
    client_publish.disconnect()

def main():
	'''
	running_publish_manager_thread = threading.Thread(target=control_command_publish, args=())
	running_publish_manager_thread.daemon = True
	running_publish_manager_thread.start()
	# 새로운 클라이언트 생성
	'''

	control_command_publish()

	# 연결 종료
	#client.disconnect()


main()