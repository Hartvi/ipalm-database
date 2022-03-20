import json
import os
import requests
from PIL import Image

ENDPOINT = "http://127.0.0.1:8000/rest/"

# IMG = r'C:/Users/jhart/PycharmProjects/ipalm-database/utilities/banana.png'
# IMG = 'C:/Users/jhart/PycharmProjects/ipalm-database/utilities/banana300.png'


def send_request(method="GET", path="/", data=None, img_path=None):
    if data is None:
        data = {}
    if img_path is not None:
        with open(img_path, 'rb') as image:
            # img_file = {"png": image}
            # data['file'] = image
            req = requests.request(method, ENDPOINT + path, auth=('jeff','jeff'), data=data, files=dict())
    else:
        req = requests.request(method, ENDPOINT + path, data=data)
    return req.text


with open('entry.json', 'r') as fp:
    entry_dict: dict = json.load(fp)
    entry_json = json.dumps(entry_dict)
    entry_data = {"entry": entry_json}
    img_path = "C:/Users/jhart/PycharmProjects/ipalm-database/tests/banana300.png"

    print("post_data:", entry_dict)
    res = send_request(method="POST", path="entries/", data=entry_data, img_path=img_path)


print(res)