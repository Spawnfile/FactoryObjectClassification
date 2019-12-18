from ctypes import *
import math
import random
import os
import cv2
import numpy as np
import time
import darknet
import socket

UDP_IP = "192.168.1.20" 
UDP_PORT = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

configPath = "/home/alper/Desktop/darknet/yolov3-tiny_obj.cfg"
weightPath = "/home/alper/Desktop/darknet/backup/alper.weights"
metaPath = "/home/alper/Desktop/darknet/data/obj.data"

cap = cv2.VideoCapture(2)

netMain = None
metaMain = None
altNames = None

def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax


def cvDrawBoxes(detections, img):
    for detection in detections:
        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
        cv2.putText(img,
                    detection[0].decode() +
                    " [" + str(round(detection[1] * 100, 2)) + "]",
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    [0, 255, 0], 2)
    try:    
        return img, pt1, pt2
    except:
        pt1 = None
        pt2 = None
        return img, pt1, pt2

if netMain is None:
    netMain = darknet.load_net_custom(configPath.encode(
        "ascii"), weightPath.encode("ascii"), 0, 1)
    metaMain = darknet.load_meta(metaPath.encode("ascii"))

darknet_image = darknet.make_image(darknet.network_width(netMain),
                                darknet.network_height(netMain),3)
line_1_1 = (int(math.ceil(darknet.network_width(netMain) / 2)) , 0)
line_1_2 = (int(math.ceil(darknet.network_width(netMain) / 2)), int(math.ceil(darknet.network_height(netMain))))
def yolo():
    if cap:    
        while True:
            prev_time = time.time()
            _, frame_read = cap.read()
            frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
            
            frame_resized = cv2.resize(frame_rgb,
                                    (darknet.network_width(netMain),
                                        darknet.network_height(netMain)),
                                    interpolation=cv2.INTER_LINEAR)
            
            darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())
            detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
            image, top_left_coordinates, bottom_right_coordinates = cvDrawBoxes(detections, frame_resized)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            #print(1/(time.time()-prev_time))
            #cv2.line(image, line_1_1, line_1_2, (255, 0, 0))
            #cv2.imshow('Demo', image) #comment after testing phase
            cv2.waitKey(3)
            return detections, image
    else:
        print("Camera Does Not Started.")

    cap.release()
    

if __name__ == "__main__":
    yolo()
