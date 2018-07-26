from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from . import read
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove


# coding=utf-8
import json
import cv2
import os
from importlib import reload
import sys
reload(sys)
# Create your views here.

batches = 64
subdiv = 8
height = 416
width = 416
rate = .001
max_batches = 500200
steps = '400000,450000'


class viaView(View):
    # def index(request):
     # return render(request, 'via.html')

    def get(self, request):
        print("hey!!")
        testView = viaView()
        # return HttpResponse("<h1>Hello from python</h1>")
        return render(request, 'via.html', {'testView': testView})

    def post(self, request):
        global subdiv, batches
        print(request.POST)
        print(subdiv, batches)
        batches = request.POST.get('batches')
        
        subdiv = request.POST.get('subdiv')
        print(subdiv, batches)
        # replace_('testScript.py', "replace_(settings,'# batch=64','batch=8')",
        #        "replace_(settings,'# batch=64','batch= " + batches + "')")

        return HttpResponse("hey from post return")


"""
        print("POST RUNNING")
        
        print(request.FILES.getlist('files[]'))
        
        if(request.FILES.getlist('files[]')) != []:
            print("Saving images")
            #print(len(data))
            data = request.FILES.getlist('files[]')
            numFiles = len(data)
            for x in range(numFiles):
                imagePathName = 'images/' + str(data[x])
                path = default_storage.save(imagePathName, ContentFile(data[x].read()))
                tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        else:
            print("Saving JSON and converting to YOLO")
            jsondata = json.loads(request.POST.get("data[]"))
            print(jsondata)
            with open('data.json', 'w') as outfile:
                json.dump(jsondata, outfile)
            convertToYolo()
       

        # print(str(data))
"""

# need
# so html file is going to have many post requests,
# starts with for loop in html file to post every picture in the array so that


def replace_(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


def test():
    print("testing outside class function")


def check_contain_chinese(check_str):
    # for ch in check_str.decode('utf-8'):
     #   if u'\u4e00' <= ch <= u'\u9fff':
     #       return True
    return False


def convertToYolo():
    imgdirname = './media/images/'
    jsonname = 'data.json'
    namefile = 'labels.names'

    # creating files and getting filenames
    lbldirname = imgdirname.rstrip('images/')+'/labels/'
    os.system('mkdir -p '+lbldirname)
    # listname = jsonname.strip('.json')
    listname = 'imagePaths'
    listdata = open(listname, 'wb')
    labelNames = open(namefile, 'w+')  # creates names file

    # for names file
    objDict = {}
    objcount = 0
    count = 0

    with open(jsonname, 'r') as f:
        data = json.loads(f.readline())
        # print data
        print(len(data))
        for key1 in data.keys():  # goes through each file

            filename = imgdirname+data[key1]['filename']  # gets file name
            print(filename, count, type(filename))
            listdata.write(filename.encode('gbk'))
            listdata.write('\n'.encode('gbk'))

            if os.path.isfile(filename):
                print("FOUNDIT")
                if check_contain_chinese(filename):
                    print(filename + ' is chinese')
                else:
                    # reading in picture
                    image = cv2.imread(
                        filename, cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_COLOR)
                    # getting second set of keys
                    rectangles = data[key1]['regions']
                    # returns number of rows columns and channels
                    height_image, width_image, _ = image.shape
                    print(len(rectangles.keys()), image.shape,
                          height_image, width_image)
                    with open(lbldirname+'/'+os.path.splitext(os.path.basename(filename))[0]+'.txt', 'w') as ff:
                        for key2 in rectangles.keys():
                            objType = rectangles[key2]["region_attributes"]
                            obj = str(objType["Animal"])
                            if not obj in objDict:
                                objDict[obj] = objcount
                                labelNames.write(obj)
                                labelNames.write(' \n')
                                objcount += 1
                            xywh = rectangles[key2]["shape_attributes"]
                            x = int(xywh["x"])
                            y = int(xywh["y"])
                            w = int(xywh["width"])
                            h = int(xywh["height"])
                            xn = float(xywh["x"])/width_image
                            yn = float(xywh["y"])/height_image
                            wn = float(xywh["width"])/width_image
                            hn = float(xywh["height"])/height_image
                            ff.write('%d %1.5f %1.5f %1.5f %1.5f\n' %
                                     (objDict[obj], xn+wn/2, yn+hn/2, wn, hn))
                            print('%d %1.5f %1.5f %1.5f %1.5f' %
                                  (objDict[obj], xn+wn/2, yn+hn/2, wn, hn))
                            image = cv2.rectangle(
                                image, (x, y), (x+w, y+h), (255, 0, 0), 1)
                    # cv2.imshow('test', image) DONT NEED TO SHOW IMAGE
                    # cv2.waitKey(0)
                    count += 1


"""

def convertToYolo():
    sys.setdefaultencoding('utf-8')
    imgdirname = './images/'
    jsonname = str(sys.argv[1])
    namefile = 'labels.names'

    # creating files and getting filenames
    lbldirname = imgdirname.rstrip('images/')+'/labels/'
    os.system('mkdir -p '+lbldirname)
    listname = jsonname.strip('.json')
    listdata = open(listname, 'wb')
    labelNames = open(namefile, 'w+') #creates names file

    objDict = {}
    objcount = 0
    count = 0
    
    with open(jsonname, 'r') as f:
        data = json.loads(f.readline())
        # print data
        print(len(data))
        for key1 in data.keys():  # goes through each file

            filename = imgdirname+data[key1]['filename']  # gets file name
            print(filename, count)
            listdata.write(filename.encode('gbk')+'\n')

            if os.path.isfile(filename):
                if check_contain_chinese(filename):
                    print(filename + ' is chinese')
                else:
                    # reading in picture
                    image = cv2.imread(
                        filename, cv2.IMREAD_IGNORE_ORIENTATION | cv2.IMREAD_COLOR)
                    # getting second set of keys
                    rectangles = data[key1]['regions']
                    # returns number of rows columns and channels
                    height_image, width_image, _ = image.shape
                    print(len(rectangles.keys()), image.shape,
                          height_image, width_image)
                    with open(lbldirname+'/'+os.path.splitext(os.path.basename(filename))[0]+'.txt', 'w') as ff:
                        for key2 in rectangles.keys():
                            objType = rectangles[key2]["region_attributes"]
                            obj = str(objType["Animal"])
                            if not objDict.has_key(obj):
                                objDict[obj] = objcount
                                labelNames.write(obj)
                                labelNames.write(' ')
                                objcount += 1
                            xywh = rectangles[key2]["shape_attributes"]
                            x = int(xywh["x"])
                            y = int(xywh["y"])
                            w = int(xywh["width"])
                            h = int(xywh["height"])
                            xn = float(xywh["x"])/width_image
                            yn = float(xywh["y"])/height_image
                            wn = float(xywh["width"])/width_image
                            hn = float(xywh["height"])/height_image
                            ff.write('%d %1.5f %1.5f %1.5f %1.5f\n' %
                                     (objDict[obj], xn+wn/2, yn+hn/2, wn, hn))
                            print('%d %1.5f %1.5f %1.5f %1.5f' %
                                  (objDict[obj], xn+wn/2, yn+hn/2, wn, hn))
                            image = cv2.rectangle(
                                image, (x, y), (x+w, y+h), (255, 0, 0), 1)
                    # cv2.imshow('test', image) DONT NEED TO SHOW IMAGE
                    # cv2.waitKey(0)
                    count += 1
"""
