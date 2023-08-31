import cv2
import sys 
if __name__ == '__main__' :

    if(len(sys.argv) < 2):
        print("input rtsp url")
    else:
        rtsp_url = "rtsp://192.168.0.28:1935/vod/mp4:/bifc/10.20.102.65_falldown_20210817210011_1629201611.mp4"
        rtsp_url =  sys.argv[1]
        video = cv2.VideoCapture(rtsp_url)

        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

        if int(major_ver)  < 3 :
            fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
            print ("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
        else :
            fps = video.get(cv2.CAP_PROP_FPS)
            print ("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

        video.release()
