'''Haar Cascade detection through OpenCV using the OpenCV documentation. This version will detect the facials of the general popuation
By Angel Rodriguez and Austin Philips 2023'''

import cv2 as cv
import os
from djitellopy import Tello
import sys

CWD = os.getcwd()
# w, h = 720, 480         # display size of the screen
# Face width value which produces accurate distance calculations
face_width = 18.5

def find_face(img):
    '''Take an input image and searches for the target object using an xml file. 
    Returns the inupt image with boundaries drawn around the detected object and the x and y values of the center of the target in the image
    as well as the area of the detection boundary.'''

    # Use Haar Cascades to detect objects using the built-in classifier tool
    cascade = cv.CascadeClassifier("haarcascade_frontalface_default.xml")
    eye_cascade = cv.CascadeClassifier('haarcascade_eye.xml')

    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    faces = cascade.detectMultiScale(gray, 1.2, 8)
    eyes = eye_cascade.detectMultiScale(gray, 1.2, 8)

    # Coordinates of center of bounding box
    faceListC = []
    faceListArea = []
    # turbineListW = []

    for (x,y,w,h) in faces:
        # draw a rectangle around the detected object
        # code for creating a rectangle to see dectection boundaries --
        cv.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # determine the center of the detection boundaries and the area
        centerX = x + w // 2
        centerY = y + h // 2
        # print(f'centerY: {centerY}')
        # print(f'h: {h}')
        # print(f'y: {y}')
        area = w * h
        faceListC.append([centerX, centerY])
        faceListArea.append(area)

        eyes = eye_cascade.detectMultiScale(gray) 
        for (ex, ey, ew, eh) in eyes:
            cv.rectangle(img, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

    if len(faceListArea) != 0:
        # if there is items in the area list, find the maximum value and return
        i = faceListArea.index(max(faceListArea))
        return img, [faceListC[i], faceListArea[i], w]
    else:
        return img, [[0, 0], 0, 0]
    

if __name__ == "__main__":
    drone = Tello()
    drone.connect()
    drone.streamon()

    # Display battery level
    battery = drone.get_battery()
    print(f'>>>>>>>>>> DRONE BATTERY: {battery}')
    if battery < 20:
        print('>>>>>>>>>> CHANGE DRONE BATTERY')
        sys.exit()

    # While loop to output the live video feed
    while True: # Output live video feed of the drone to user until face has been detected a certein number of times    
        frame = drone.get_frame_read()
        img = frame.frame
        # img = cv.resize(img, (w, h))
        img, info = find_face(img)
        # img, info = find_face(img)
        # Display output window showing the drone's camera frames
        cv.imshow("Drone Live Video (say cheese)", img)
        cv.waitKey(1)

        x, y = info[0]  # The x and y location of the center of the bounding box in the frame
        area = info[1]  # The area of the bounding box
        width = info[2] # The width of the bounding box

        if info[0][0]: # Face detected
            # (Focal length of camera lense * Real-world width of object)/Width of object in pixels
            # About 22 cm correctly calculates the distance of my face, feel free to revise to work with you
            print(f'>>>>>>>>>>> FACE DETECTED')
