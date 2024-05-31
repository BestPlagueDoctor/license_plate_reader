import os
import cv2
import imutils
import numpy as np
from imutils.video import FPS
from imutils.video import VideoStream
from pathlib import Path
import pytesseract
from PIL import Image

def ocr(plate):
    return pytesseract.image_to_string(plate, lang='eng', config='--psm 12')

w, h = 416, 416

thresh = 0.4
class_file = "data/classes.txt"
classes = None
with open(class_file,  'rt') as f:
    classes = f.read().rstrip('\n').split('\n')
model_config = "cfg/yolov3-custom.cfg"
model_weights = "backup/yolov3-custom_final.weights"

net = cv2.dnn.readNetFromDarknet(model_config, model_weights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

ln = net.getLayerNames()
ln = [ln[i-1] for i in net.getUnconnectedOutLayers()]

p = Path('./vids')
for vid in p.glob("*.avi"):
    vid = str(vid)
    vid_path = Path(str(vid[:-4]))
    try:
        vid_path.mkdir(parents=False, exist_ok=False)
    except FileExistsError:
        print("already processed file " + str(vid_path))
    vidcap = cv2.VideoCapture(vid)
    success, frame = vidcap.read()
    count = 0
    while success:
        boxes = []
        confidences = []
        blob = cv2.dnn.blobFromImage(frame, 1.0/255.0, (416, 416),  crop=False)
        net.setInput(blob)
        H, W = frame.shape[:2]
        layer_outs = net.forward(ln)
        for output in layer_outs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                if confidence > thresh:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    tlx = int(centerX - (width/2))
                    tly = int(centerY - (width/2))
                    boxes.append([tlx, tly, int(width), int(height)])
                    confidences.append(float(confidence))
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, thresh, thresh)
        if len(idxs) > 0 and idxs.any() != [0]:
            for i in idxs.flatten():
                print(count)
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                if x < 0:
                    x = 0
                if y < 0:
                    y = 0
                if x + w > W:
                    w = W-x
                if y + h > H:
                    h = H-y
                gry = cv2.cvtColor(frame[y-20:y+h+20,x:x+w], cv2.COLOR_BGR2GRAY)
                erd = cv2.erode(gry, None, iterations=1)
                erd = cv2.GaussianBlur(erd, (5,5), 0)
                #ret, plate_iso_reg = cv2.threshold(erd, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                plate_iso = cv2.adaptiveThreshold(erd, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  cv2.THRESH_BINARY, 21, 5)
                ret, plate_iso_otsu = cv2.threshold(erd, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
                #cv2.imwrite(str(vid_path) + "/frame_gray_reg%d.jpg" % count, plate_iso_reg)
                cv2.imwrite(str(vid_path) + "/frame_gauss%d.jpg" % count, plate_iso_otsu)
                plate_num = (ocr(plate_iso_otsu))
                print(plate_num)
                frame = cv2.rectangle(frame, (x,y), (x+w, y+h), [36,255,12], 2)
                text = "{}: {:.4f} {}".format(classes[0], confidences[i], plate_num)
                cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, [255,255,255], 2)
                cv2.imwrite(str(vid_path) + "/frame%d.jpg" % count, frame)
        success, frame = vidcap.read()
        count += 1

