import json
import os
import requests
from PIL import Image

ENDPOINT = "http://127.0.0.1:8000/rest/"

# IMG = r'C:/Users/jhart/PycharmProjects/ipalm-database/utilities/banana.png'
IMG = 'C:/Users/jhart/PycharmProjects/ipalm-database/utilities/banana300.png'


def send_request(method="GET", path="/", data=None, img_path=None):
    if data is None:
        data = {}
    if img_path is not None:
        with open(img_path, 'rb') as image:
            img_file = {"png": image}
            # data['file'] = image
            req = requests.request(method, ENDPOINT + path, auth=('jeff','jeff'), data=data, files=img_file)
    else:
        req = requests.request(method, ENDPOINT + path, data=data)
    return req.text


with open('setup.json', 'r') as fp:
    setup_dict = json.load(fp)
    setup_json = json.dumps(setup_dict)
    setup_data = {"setup": setup_json}

    print("post_data:", setup_dict)
    res = send_request(method="POST", path="measurements/", data=setup_data, img_path=IMG)


print(res)