import cv2
import imutils
import numpy as np
from PIL import Image
import json
from os.path import dirname, join
import base64
import io

ans = " "
def get_output_layers(net):
    layer_names = net.getLayerNames()

    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    return output_layers


def draw_prediction(img, class_id, classes, COLORS, confidence, x, y, x_plus_w, y_plus_h):
	label = str(classes[class_id])

	color = COLORS[class_id]

	cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)

	cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
	global ans
	ans = label



def YOLO_Detect(img):
	classess = join(dirname(__file__), 'yolov3_custom.txt')
	config =  join(dirname(__file__),'yolov3_custom.cfg')
	weights =  join(dirname(__file__),'yolov3_custom_last.weights')
	#img = join(dirname(__file__),'6.jpg')

	classes = None

	with open(classess, 'r') as f:
	    classes = [line.strip() for line in f.readlines()]

	COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

	image = img
	image = cv2.resize(image, (640, 480))

	Width = image.shape[1]
	Height = image.shape[0]
	scale = 0.00392

	net = cv2.dnn.readNet(weights, config)

	blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)

	net.setInput(blob)

	outs = net.forward(get_output_layers(net))

	class_ids = []
	confidences = []
	boxes = []
	conf_threshold = 0.5
	nms_threshold = 0.4

	for out in outs:
	    for detection in out:
	        scores = detection[5:]
	        class_id = np.argmax(scores)
	        confidence = scores[class_id]
	        if confidence > 0.5:
	            center_x = int(detection[0] * Width)
	            center_y = int(detection[1] * Height)
	            w = int(detection[2] * Width)
	            h = int(detection[3] * Height)
	            x = center_x - w / 2
	            y = center_y - h / 2
	            class_ids.append(class_id)
	            confidences.append(float(confidence))
	            boxes.append([x, y, w, h])

	indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

	for i in indices:
	    i = i[0]
	    box = boxes[i]
	    x = box[0]
	    y = box[1]
	    w = box[2]
	    h = box[3]
	    draw_prediction(image, class_ids[i], classes, COLORS, confidences[i], round(x), round(y), round(x + w),
	                    round(y + h))


def test(img):
    #image = np.asarray(bytearray(img.read()), dtype="uint8")
    #image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    #nparr = np.fromstring(img, np.uint8)
    #image = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # cv2.IMREAD_COLOR in OpenCV 3.1
    pic = Image.open(io.BytesIO(bytes(img)))
    open_cv_image = np.array(pic)
    # Convert RGB to BGR
    frame = open_cv_image[:, :, ::-1].copy()
    im = imutils.resize(frame, width=min(300, frame.shape[1]))
    YOLO_Detect(im)
   

    
    return ans
