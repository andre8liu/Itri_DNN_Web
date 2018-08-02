from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
#from . import read
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import subprocess
from subprocess import Popen, PIPE
# Create your views here.

import json
import cv2
import os
from importlib import reload
import sys
import time
reload(sys)




#things to fix
#DONEconfigering learning rate
#LATERforcing first table to be 'Objects'
#DONEremoving images dir then making new one
#adding training command


class jsonToYolo(View):
    def get(self,request):
        print("hey")
        yoloView = jsonToYolo()
        return render(request, 'jsontoyolo.html', {'yoloView':yoloView}) 


    def post(self,request):
        
        print("Saving JSON and converting to YOLO")
        jsondata = json.loads(request.POST.get("data[]"))
        print(jsondata)
        with open('data.json', 'w') as outfile:
            json.dump(jsondata, outfile)
        convertToYolo()
        print("BEFORE START DOCKER")
        startDocker()
        print("AFTER START DOCKER")
        
        return HttpResponse("hey from post return")



def check_contain_chinese(check_str):
    # for ch in check_str.decode('utf-8'):
     #   if u'\u4e00' <= ch <= u'\u9fff':
     #       return True
    return False


def convertToYolo():
    imgdirname = './media/images/'
    dockimgdir = './trainData/images/'
    jsonname = 'data.json'
    namefile = 'labels.names'

    # creating files and getting filenames
    lbldirname = imgdirname.rstrip('images/')+'/labels/'

    #subprocess.call(['rm','-rf',imgdirname])
    #subprocess.call(['mkdir','-p',imgdirname])
    subprocess.call(['mkdir','-p',lbldirname])

    #os.system('mkdir -p '+lbldirname)
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
            filepath = dockimgdir +data[key1]['filename']
            print(filename, count, type(filename))
            listdata.write(filepath.encode('gbk'))
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


def startDocker():
    # starting docker
    subprocess.call(['docker', 'kill', 'darknet'])
    subprocess.call(['docker', 'rm', 'darknet'])
    subprocess.call(['nvidia-docker', 'run', '-it', '-d',
                 '--name', 'darknet', 'blitzingeagle/darknet'])

    # tranfering images
    subprocess.call(['docker', 'cp', 'media', 'darknet:usr/local/src/darknet'])
    # transfering labels
    subprocess.call(['docker', 'cp', 'med/labels',
                 'darknet:usr/local/src/darknet'])
    # transfering names file
    subprocess.call(['docker', 'cp', 'labels.names',
                 'darknet:usr/local/src/darknet'])
    # transfering image paths
    subprocess.call(['docker', 'cp', 'imagePaths',
                 'darknet:usr/local/src/darknet'])
    # transfer script to docker
    subprocess.call(['docker','cp','copy_dockerScript.py','darknet:/usr/local/src/darknet'])
    #time.sleep(10)
    print("BEFORE DS CALL")
    subprocess.call(['nvidia-docker', 'exec', '-it',
                'darknet', 'python', 'copy_dockerScript.py'])
    print("AFTER DS CALL")
