import sys
import cv2

def read_cam():
    cap = cv2.VideoCapture("uridecodebin3 uri=rtspt://admin:1111@irumdnt.okddns.com:5445/Stream1/Channel=6")
    if cap.isOpened():
        cv2.namedWindow("demo", cv2.WINDOW_AUTOSIZE)
        while True:
            ret_val, img = cap.read()
            cv2.imshow('demo',img)
            cv2.waitKey(10)
    else:
     print("rtsp open failed")

    cv2.destroyAllWindows()


if __name__ == '__main__':
    read_cam()