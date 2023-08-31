import cv2
import time
import os
import sys
uri = "rtspt://admin:admin@192.168.0.110/1/profile"
uri = "rtspt://admin:1111@irumdnt.okddns.com:5445/Stream1/Channel=3"
cap = "rtspsrc location=%s ! rtph264depay ! h264parse ! avdec_h264 ! videoconvert ! appsink" % uri

cap = cv2.VideoCapture(cap, cv2.CAP_GSTREAMER)
frame_num = 0
tic = time.time()
while True:
    frame_num += 1
    ret, frame = cap.read()
    if ret:
        pass
    if not cap.isOpened():
        sys.exit("Failed to open camera!")
    if frame_num == 1000:
        break
toc = time.time()
print("Decode FPS: %.2f" % (frame_num / (toc - tic)))

cap.release()
