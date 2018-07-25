import subprocess
from subprocess import Popen, PIPE


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
subprocess.call(['docker','cp','testScript.py','darknet:/usr/local/src/darknet'])
subprocess.call(['nvidia-docker', 'exec', '-it',
                 'darknet', 'python', 'testScript.py'])
