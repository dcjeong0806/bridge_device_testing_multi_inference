import sys
import gi
import datetime 
import time 
from gi.repository import Gst, GstRtspServer, GObject
#from common.bus_call import bus_call
import paho.mqtt.client as mqtt 
import hashlib
import json
import subprocess
gi.require_version('Gst', '1.0')


current_milli_time = lambda: int(round(time.time() * 1000))


class MyFactory(GstRtspServer.RTSPMediaFactory):
    rtspurl = ""
    global pipeline 
    def __init__(self,url):
        global rtspurl
        global pipeline
        rtspurl = url
        print("111111" + rtspurl)
        GstRtspServer.RTSPMediaFactory.__init__(self)

    def do_create_element(self, url):
        print("URL ++++" + str(rtspurl))
        spec = " uridecodebin uri=" + rtspurl + " is-live=1 ! nvvidconv ! nvv4l2h264enc insert-sps-pps=1 insert-vui=1 ! rtph264pay name=pay0 pt=96"   

        #spec = " videotestsrc is-live=1 ! video/x-raw,width=1280,height=720,framerate=30/1 ! nvvidconv ! nvv4l2h264enc insert-sps-pps=1 insert-vui=1 ! rtph264pay name=pay0 pt=96"    # h264 format -> h264 format
        #caps = Gst.ElementFactory.make("capsfilter", "filter")
        #convert_string = "video/x-raw(memory:NVMM),width={},height={},format=I420".format("640","360")
        #caps.set_property("caps",Gst.Caps.from_string(convert_string))
        pipeline = Gst.parse_launch(spec) 
     
        #pipeline.add(caps)

        #gst-launch-1.0 uridecodebin uri=rtspt://172.30.1.250:1935/vod/mp4:/face/helmet.mp4 is-live=1 ! video/x-raw,width=640,height=360,framerate=30/1,format=I420 ! nvvidconv ! nvv4l2h264enc insert-sps-pps=1 insert-vui=1 ! rtph264pay name=pay0 pt=96
        return pipeline 

class GstServer():
    def __init__(self,url,port,uri):
        print(url,port,uri,bdnumber)
        self.server = GstRtspServer.RTSPServer()
        bridge_port = 9999
        self.server.set_service(bridge_port)
        factory = MyFactory(url)

        caps = Gst.ElementFactory.make("capsfilter", "filter")
        convert_string = "video/x-raw(memory:NVMM),width={},height={},format=I420".format("640","360")
        caps.set_property("caps",Gst.Caps.from_string(convert_string))
      
       
        updsink_port_num = 5400
        codec = "H264"
        factory.set_launch(
            '( udpsrc name=pay0 port=%d buffer-size=524288 caps="application/x-rtp, media=video, %s , clock-rate=90000, encoding-name=(string)%s, payload=96 " )'
            % (updsink_port_num, convert_string, codec) 
        )
        factory.set_shared(True)
        m = self.server.get_mount_points()
        m.add_factory("/" + uri, factory)
        self.server.attach(None)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)

if __name__ == '__main__':
    #print("##########",sys.argv)
    if(len(sys.argv) > 5):
        GObject.threads_init()
        Gst.init(None)
        loop = GObject.MainLoop()
        ####### 
        '''
        1 : rtsp url 
        2 : port 
        3 : uri 
        '''

        rtsp_url = sys.argv[1]
        port = sys.argv[2]
        uri = sys.argv[3]
        key = sys.argv[4]
        bdnumber = sys.argv[5]
        uri_key = uri + key

        secret_uri = hashlib.sha256(uri_key.encode()).hexdigest()
        #port = str(10009)
        #secret_uri = "01a1a6dad62fccaf209802240502412b64f0ceab43fc7494bacdd1b74105eea3"
        s = GstServer(rtsp_url,port,secret_uri)
        #bus = s.get_bus()
        #bus.add_signal_watch()
        #bus.connect("message",bus_call,loop)
        #s = GstServer("rtspt://172.30.1.250:1935/vod/mp4:/face/helmet.mp4")
        
        client_publish = mqtt.Client()
        client_publish.on_connect = on_connect
        client_publish.on_disconnect = on_disconnect
        client_publish.on_publish = on_publish
        client_publish.connect('20.194.104.191', 1883)
        topic_name = "/RESPONSE/STREAMING/" + uri
        return_rtsp_url = ":" + str(port) + "/" + secret_uri 

        print(topic_name, return_rtsp_url)

        command = {
            "Port" : port,
            "SubUrl" : secret_uri
        }

        print(command)

        client_publish.publish(topic_name,json.dumps(command) , 1)
        client_publish.disconnect()  

        try:
            loop.run()
        except Exception as ex:
            print("###### PIPELINE GET STATE = ", ex)

    else:
        sys.exit()


