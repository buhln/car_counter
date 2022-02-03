# -*- coding: utf-8 -*-
#
# Car counter BGsub
# =================
# Program counts cars on a video stream and uploads the
# counts to Thingspeak.com. It differentiates between the
# direction of travel
#
# In Debug Mode (postfix -d) a file output.avi is saved with marked image crop
#
# by Nico Buhl, 2021-22
#
# Inspired by
# https://www.youtube.com/watch?v=HXDD7-EnGBY
#

import cv2
import sys
from tracker_BGsub import EuclideanDistTracker
import time
import http.client
import numpy as np
from gpiozero import CPUTemperature

#  Check if Debug Mode is activated
if len(sys.argv) == 2 and sys.argv[1] == '-d':
    debugmode = True
    print("Debug mode active!")
else:
    debugmode = False

def transferTS(field_str):
    key = "HERE_YOUR_THINGSPEAK_WRITEKEY"
    while True:
        cputemp = round(CPUTemperature().temperature,2)
        params = field_str+"&field8="+str(cputemp)+"&key="+key
        headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = http.client.HTTPConnection("api.thingspeak.com:80")
        try:
            conn.request("POST", "/update", params, headers)
            response = conn.getresponse()
            print (response.status, response.reason)
            conn.close()
            status = True
        except:
            print ("connection failed")
            status = False
        break
    return status

# used to record the time when we processed last frame
prev_frame_time = 0
# used to record the time at which we processed current frame
new_frame_time = 0

# Time between Thingspeak uploads in seconds
timetouploadTS = 60 * 5

# Define picture crop -> Check in debug mode!
roixy = [ 470, 675, 200, 337 ]   # X1, X2, Y1, Y2

# Tracker objects
tracker = EuclideanDistTracker(roixy)

cap = cv2.VideoCapture(0)
cap.set(3,1280)
cap.set(4,720)

# If Debug Mode activated save videostream
if debugmode == True:
    # Definition Video speichern
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, size)  

# Object detection from stable camera
object_detector = cv2.createBackgroundSubtractorMOG2(history=750, varThreshold=250) # History=100 Threshold=250

# Start timer for upload measurements to TS
last_TS_transfer = time.perf_counter()

while True:
    if debugmode == True:
        start_timer = time.perf_counter()
        print("===== NEW FRAME =====")

    _,frame = cap.read()
    frame = cv2.rotate(frame, cv2.ROTATE_180)
 
    # Extract region of interest
    roi = frame[roixy[2]:roixy[3],roixy[0]:roixy[1]]

    # Object Detection
    mask = object_detector.apply(roi)
    # _, mask = cv2.threshold(mask, 240,255, cv2.THRESH_BINARY)
    dilkernel = np.ones((5,5),np.uint8)
    mask = cv2.dilate(mask,dilkernel,iterations = 2)
    
    contours,_ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    
    for cnt in contours:
        # Calculate area and remove small elements
        area = cv2.contourArea(cnt)
        if area > 5000:
            cv2.drawContours(roi, [cnt], -1, (0,0,255), 1)
            x,y,w,h = cv2.boundingRect(cnt)
            tracker.detections.append([x,y,w,h])
        
    # Object tracking
    boxes_ids = tracker.update()
    
    # Show Boxes and IDs
    for box_id in boxes_ids:
        x, y, w, h, id = box_id
        if debugmode == True:
            cv2.putText(roi, str(id), (x,y-15), cv2.FONT_HERSHEY_PLAIN, 2, (255,0,0), 2)
            cv2.rectangle(roi,(x,y),(x+w,y+h),(0,255,0),3)
        
            # Calc center of rectangular
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            cv2.circle(roi, (cx,cy), 5, (0,255,0), 2)
            cv2.putText(roi, str(cx), (cx,cy-15), cv2.FONT_HERSHEY_PLAIN, 2, (0,255,0), 1)
    
        
    # Check timer for upload to TS
    if time.perf_counter() - last_TS_transfer > timetouploadTS:
        print("SEND TO THINGSPEAK.com")
        # Transmit car counter
        carrate = round(sum(tracker.counter) * 60*60 / timetouploadTS)
        field_url = "field1="+str(tracker.counter[0])+"&field2="+str(tracker.counter[1])+"&field3="+str(carrate)   
        if transferTS(field_url) == True:
            tracker.counter_all += tracker.counter
            tracker.resetCounter()
            print("Counter all cars    : "+str(tracker.counter_all))
        
        last_TS_transfer = time.perf_counter()
    # End function transfer to TS
    
    
    if debugmode == True:
        # Show line at which the car is counted
        cv2.rectangle(frame,[roixy[0],roixy[2]],[roixy[1],roixy[3]],
                      color=(0,0,255),thickness=2)   
        cv2.line(frame, (int((roixy[1]-roixy[0])/2)+roixy[0], 0), 
                   (int((roixy[1]-roixy[0])/2)+roixy[0], 720), (0, 0, 255), thickness=2)    
        # Save video
        out.write(frame)
    
    
    # Time when we finish processing for this frame
    new_frame_time = time.time()

    if debugmode == True:
    # Calculating the fps
    # fps will be number of frame processed in given time frame
    # since their will be most of time error of 0.001 second
    # we will be subtracting it to get more accurate result
        fps = 1/(new_frame_time-prev_frame_time)
        print("fps                  : " + str(round(fps, 2)))

    prev_frame_time = new_frame_time
    
