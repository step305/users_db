from __future__ import print_function
import requests
import json
import cv2
import face_recognition
from backend.utils import utils

img = cv2.imread('test.jpg')
_, jpg = cv2.imencode('.jpg', img)
json_img = utils.jpeg2str(jpg.tobytes())

enc = face_recognition.face_encodings(img)[0]
json_enc = utils.encoding2str(enc.tobytes())

response = requests.post('http://127.0.0.1:8000/api/add_new', data={'image': json_img, 'name': 'new_name1',
                                                                    'card_id': '00000'})
print(json.loads(response.text))

for i in range(10):
    response = requests.post('http://127.0.0.1:8000/api/add_photo', data={'image': json_img, 'name': 'new_name1',
                                                                          'encoding': json_enc})
    print(json.loads(response.text))

response = requests.post('http://127.0.0.1:8000/api/get_face', data={'name': 'new_name1'})
face = utils.str2jpeg(json.loads(response.text)['face'])
face_img = cv2.imdecode(face, cv2.IMREAD_COLOR)
cv2.imshow('a', face_img)
while cv2.waitKey(1) != 27:
    continue

response = requests.post('http://127.0.0.1:8000/api/get_names', data={})
print(json.loads(response.text)['users'])

response = requests.post('http://127.0.0.1:8000/api/get_card', data={'name': 'new_name1'})
print(json.loads(response.text)['card_id'])

response = requests.post('http://127.0.0.1:8000/api/rm_model', data={'model_id': 1})
print(json.loads(response.text))

response = requests.post('http://127.0.0.1:8000/api/train_model', data={})
print(json.loads(response.text))

response = requests.post('http://127.0.0.1:8000/api/get_model', data={})
model = utils.str2model(json.loads(response.text)['model'])
print(model.predict([enc]))
