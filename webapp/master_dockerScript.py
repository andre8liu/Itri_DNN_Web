import subprocess
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
from subprocess import Popen, PIPE


# subprocess.call("ls")
# subprocess.Popen("ls")

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

"""
Files:  cfg/coco.data
        cfg/yolo-v2.cfg

things needed to config:
    1. classes in multiple files --> need to get number of classes
    2. steps --> 3000,6000
    3. batchs --> testing: 8
    4. subdivisions --> testing: 1
    5. height + width --> 416,416
    6. learning_rate --> same
    7. max_batches --> 10,000
    8. names/images paths --> 
"""

# changing stuff in yolo-v2.cfg
#   1. batch=1 --> comment out
#   2. subdivisions=1 --> comment out
#   3. # batch=64 - > batch=8
#
#   replace opens file, need to get # of classes
#   post is going to call script in docker to config files


######### script in docker to configure files runs in docker############
##file will be cped into docker and run


#create datafolder and move images/labels
subprocess.call(['mkdir','trainData'])
subprocess.call(['mv','labels','trainData/labels'])
subprocess.call(['mv','media/images','trainData/images'])


settings = 'cfg/yolov2.cfg'
paths = 'cfg/coco.data'
p = subprocess.Popen(['wc','-l','labels.names'], stdout = PIPE)
numClasses = p.stdout.read()
#print(type(numClasses))
#classes = numClasses.rstrip('labels.names')
classes = numClasses[0]
print(classes)


#for yolov2.cfg
replace_(settings,'batch=1','#batch=1') #commenting out testing config
replace_(settings,'subdivisions=1','#subdivisions=1') #commenting out testing config
replace_(settings,'# batch=64','batch=8')
replace_(settings,'# subdivisions=8','subdivisions=1')
replace_(settings,'max_batches = 500200','max_batches = 10000')
replace_(settings,'steps=400000,450000','steps=3000,6000')
replace_(settings,'classes=80','classes=' + classes)
replace_(settings,'width=416','width=416')
replace_(settings,'height=416','height=416')
replace_(settings,'scales=.1,.1','scales=.1,.1')
replace_(settings,'learning_rate=0.001','learning_rate=0.001')


#for coco.data
replace_(paths,'classes= 80','classes=' + classes)
replace_(paths,'train  = /home/pjreddie/data/coco/trainvalno5k.txt','train= imagePaths')
replace_(paths,'valid = data/coco_val_5k.list','valid = imagePaths')
replace_(paths,'names = data/coco.names', 'names = labels.names')

subprocess.call(['wget','https://pjreddie.com/media/files/darknet19_448.conv.23'])
subprocess.call(['./darknet','detector','train','cfg/coco.data','cfg/yolov2.cfg','darknet19_448.conv.23'])



# replace_('changing.txt','CHANGE','CHANGED!!')
# subprocess.Popen(['cat','changing.txt'])

#p=subprocess.Popen(['nvidia-docker', 'run','-it', '--name', 'test', 'blitzingeagle/darknet', '/bin/bash'], stderr = PIPE)
#p = subprocess.Popen(['nvidia-docker', 'run','-it','blitzingeagle/darknet', 'pwd'],stdout=PIPE)
# subprocess.Popen('nvidia-docker')
#output = p.stderr.read()
# print(output)

# subprocess.Popen('exit')
#print("WE OUT")


"""
Script after converting to yolo format:
    if we use docker:
        1. need to start the docker 

        2.then we need to transfer images,names file, image path file, 
        json yolo annotations file from server -> docker
        
        3.then we need to configure the files from outside of the container
        and run yolo to train

        we can also try to see if scripts will continue executing when entering container
        
"""


def start_docker():
    # starting docker
    subprocess.call(['docker', 'kill', 'darknet'])
    subprocess.call(['docker', 'rm', 'darknet'])
    subprocess.call(['nvidia-docker', 'run', '-it', '-d','--name', 'darknet', 'blitzingeagle/darknet'])

    # tranfering images
    subprocess.call(['docker', 'cp', 'media', 'darknet:usr/local/src/darknet'])
    # transfering labels
    subprocess.call(['docker', 'cp', 'med/labels', 'darknet:usr/local/src/darknet'])
    # transfering names file
    subprocess.call(['docker', 'cp', 'labels.names','darknet:usr/local/src/darknet'])
    # transfering image paths
    subprocess.call(['docker', 'cp', 'imagePaths','darknet:usr/local/src/darknet'])
    # transfer script to docker


#DONEmoving save json/converingyolo/transfering data to server/ and runnning docker scripts 
#another page

#DONEvia views.py post request should handle saving data from forms (using replace to change file scripts)
#and saving images

#finish fixing post function to change files on save click
#DONEfix image pathing

#change html pages on click for save as json