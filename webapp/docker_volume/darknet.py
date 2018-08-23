from ctypes import *
import math
import random
import sys
import json
import os


def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1


def c_array(ctype, values):
    return (ctype * len(values))(*values)


class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]


class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]


#lib = CDLL("/home/pjreddie/documents/darknet/libdarknet.so", RTLD_GLOBAL)
lib = CDLL("/usr/local/src/darknet/libdarknet.so", RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

make_boxes = lib.make_boxes
make_boxes.argtypes = [c_void_p]
make_boxes.restype = POINTER(BOX)

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

num_boxes = lib.num_boxes
num_boxes.argtypes = [c_void_p]
num_boxes.restype = c_int

make_probs = lib.make_probs
make_probs.argtypes = [c_void_p]
make_probs.restype = POINTER(POINTER(c_float))

detect = lib.network_predict
detect.argtypes = [c_void_p, IMAGE, c_float, c_float,
                   c_float, POINTER(BOX), POINTER(POINTER(c_float))]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)

network_detect = lib.network_detect
network_detect.argtypes = [c_void_p, IMAGE, c_float,
                           c_float, c_float, POINTER(BOX), POINTER(POINTER(c_float))]

# show_image = lib.show_image
# show_image.argtypes = [IMAGE, c_char_p]
#
# cvWaitKey = lib.cvWaitKey
# cvWaitKey.argtypes = [c_int]
#
# cvDestroyAllWindows = lib.cvDestroyAllWindows
# cvDestroyAllWindows.argtypes = []

"""
show_image(im, "predictions");
cvWaitKey(0);
cvDestroyAllWindows();
"""


def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        res.append((meta.names[i], out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res

# only works on one picture so can we make it work on multiple pics?
# name:rect
# x:boxes[j].x
# y:boxes[j].y


def create_region(reg_num, x, y, width, height, obj):
    reg_num = str(reg_num)

    region = {
        'shape_attributes': {
            'name': 'rect',
            'x': x,
            'y': y,
            'width': width,
            'height': height
        },
        'region_attributes': {
            'Animal': obj
        }
    }
    return region


def create_file_reg(filename, size):
    #size = os.path.getsize(path)
    #fullname = filename + str(size)
    file_reg = {
            'fileref': '',
            'size': size,
            'filename': filename,
            'base64_img_data': '',
            'file_attributes': {}
    }
    return file_reg


def detect(net, meta, image,filename, thresh=.5, hier_thresh=.5, nms=.45):
    im = load_image(image, 0, 0)
    #print(os.path.getsize('/usr/local/src/darknet/data/horses.jpg'))
    boxes = make_boxes(net)
    probs = make_probs(net)
    num = num_boxes(net)
    network_detect(net, im, thresh, hier_thresh, nms, boxes, probs)
    
    file_reg = create_file_reg(filename,size)
    reg = {}
    #print(image)
    # call function to create entire picture block
    # for just one picture
    reg_num = 0
    for j in range(num):
        for i in range(meta.classes):
            if probs[j][i] > 0:  # if a bounding box is found
                
                # res.append((meta.names[i].decode("utf-8"),
                #           probs[j][i], (boxes[j].x, boxes[j].y, boxes[j].w, boxes[j].h)))
                x = boxes[j].x - ((boxes[j].w)/2)
                y = boxes[j].y - ((boxes[j].h)/2)

                reg[str(reg_num)] = (create_region(
                    reg_num, x, y, boxes[j].w, boxes[j].h, meta.names[i].decode("utf-8")))
                reg_num += 1
                # CALL HELPER THAT CREATES REGION USING INFO GIVEN ^^

    file_reg['regions'] = reg
    #res = sorted(res, key=lambda x: -x[1])
    #print("this is num" + str(num))
    #print("this is meta.classes" + str(meta.classes))
    free_image(im)
    free_ptrs(cast(probs, POINTER(c_void_p)), num)
    return file_reg  # return block


if __name__ == "__main__":
    #net = load_net("cfg/densenet201.cfg", "/home/pjreddie/trained/densenet201.weights", 0)
    #im = load_image("data/wolf.jpg", 0, 0)
    #meta = load_meta("cfg/imagenet1k.data")
    #r = classify(net, meta, im)
    # print r[:10]
    #filename = 'horses.jpg'
    net = load_net(b"cfg/yolov2.cfg", b"weights/yolov2.weights", 0)
    meta = load_meta(b"cfg/coco.data")
    r = {}
    with open('./pre_imagepaths') as f:
        for line in f:
            line = line.rstrip('\n')
            filename = os.path.basename(line)
            size = os.path.getsize(line)
            fullname = filename+ str(size)
            #print(line)
            r[fullname] = detect(net, meta, line.encode('utf-8'),filename)
            
    with open('pre_annot.json','w') as outfile:
        json.dump(r,outfile)
    #print(r)
    #path = 'data/horses.jpg'
    #r = detect(net, meta, path.encode('utf-8'),"horses.jpg")
    # we can make a seperate imagepaths file for the inf images and pass them in here
    # and load them one by one and keep adding
    

    #r = detect(net, meta, b"data/dog.jpg")
    # print(r)
    # make another function that calls detect that adds to res then pushes to file!!!

# for each meta.class, if prob >0 then create a 'region' for that object bounding box.
# helper function create_region
# can create each object in the main function

# i think this should create the whole thing then
