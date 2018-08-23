import json


# key pair values for each shape attribute?
# its not always going to be a rectangle
# name is given

# shape attributes: name, x, y, width, heightn
# region_attributes: should only be object
# should have a region for each bb
# need to limit shapes to only boxes

data = {}
pic1 = '0.jpg12213'
#data[pic1] = []
w = str(243)
data[pic1] = {
    'size': 12213,
    'filename': '0.jpg',
    'file_attributes': {},
    'regions': [{
        'shape_attributes': {
            'name': 'rect',
            'x': 101,
            'y': 13,
            'width': 282,
            'height': 251
        },
        'region_attributes': {
            'Object': 'cat'
        }
    }]
}
'''
#data['secondfile.jpg'] = {}
data['secondfile.jpg'] = {
    'fileref': '',
    'size': '34448',
    'filename': '00.jpg',
    'base64_img_data': '',
    'file_attributes': {},
    'regions': {}
}
'''

with open('testjson.json', 'w') as outfile:
    json.dump(data, outfile)

print("Success!")
