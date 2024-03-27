import os
import cv2
from cvzone.HandTrackingModule import HandDetector
import numpy as np

# variables
width, height = 1280, 720
folderPath = "images"

# camera setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# get list of presentation images
pathImages = sorted(os.listdir(folderPath), key=len)
print(pathImages)

# variables
imgNumber = 0
hs, ws = int(120*1), int(213*1)
gestureThreshold = 300
buttonPressed = False
buttonCount = 0
buttonDelay = 30
annotations = [[]]
annotationNumber = 0
annotationStart = False
cameraStart = False

# hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

while True:
    # import Images
    success, img = cap.read()
    img = cv2.flip(img, 1)
    pathFullImage = os.path.join(folderPath, pathImages[imgNumber])
    imgCurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img)
    cv2.line(img, (0, gestureThreshold), (width, gestureThreshold), (0, 255, 0), 10)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        # constraint values for easier drawing

        xVal = int(np.interp(lmList[8][0],[width // 2, w], [0, width]))
        yVal = int(np.interp(lmList[8][1], [150, height-200], [0, height]))
        print(fingers)
        indexFinger = xVal, yVal # to get index finger

        if cy <= gestureThreshold:
            # gesture 1- left
            if fingers == [1, 0, 0, 0, 0]:
                print("Left")
                annotationStart = False
                if imgNumber > 0:
                    buttonPressed = True
                    imgNumber -= 1
                    annotations = [[]]
                    annotationNumber = 0


            # gesture 2- right
            if fingers == [0, 0, 0, 0, 1]:
                print("Right")
                annotationStart = False
                if imgNumber < len(pathImages)-1:
                    buttonPressed = True
                    imgNumber += 1
                    annotations = [[]]
                    annotationNumber = 0

            # gesture 6- camera mode
            if fingers == [0, 1, 1, 1, 1]:
                print("camera")
                buttonPressed = True
                if cameraStart == False:
                    cameraStart = True

                else:
                    cameraStart = False





        # gesture 3- show pointer
        if fingers == [0, 1, 1, 0, 0]:
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotationStart = False

        # gesture 4- draw
        if fingers == [0, 1, 0, 0, 0]:
            if annotationStart is False:
                annotationStart = True
                annotationNumber += 1
                annotations.append([]) # adding empty list
            cv2.circle(imgCurrent, indexFinger, 12, (0, 0, 255), cv2.FILLED)
            annotations[annotationNumber].append(indexFinger)

        else:
            annotationStart = False

        # gesture 5- erase
        if fingers == [0, 1, 1, 1, 0]:
            if annotations:
                if annotationNumber >= 0:
                    annotations.pop(-1)
                    annotationNumber -= 1
                    buttonPressed = True




    # Button Pressed iteration
    if buttonPressed:
        buttonCount += 1
        if buttonCount > buttonDelay:
            buttonCount = 0
            buttonPressed = False

    for i in range (len(annotations)):
        for j in range(len(annotations[i])):
            if j != 0:
                cv2.line(imgCurrent, annotations[i][j-1], annotations[i][j], (0, 0, 200), 12)




    # adding webcam image on slide
    imgSmall = cv2.resize(img,(ws,hs))
    h, w, _ = imgCurrent.shape
    imgCurrent[0:hs, w-ws:w] = imgSmall
    if cameraStart == False:
        cv2.imshow("Slides", imgCurrent)
        if(cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) > 0):
            cv2.destroyWindow("Image")
    else:
        cv2.imshow("Image", img)
        if (cv2.getWindowProperty("Slides", cv2.WND_PROP_VISIBLE) > 0):
            cv2.destroyWindow("Slides")

    key = cv2.waitKey(1)
    if key == ord('q'):
        break