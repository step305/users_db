from backend.db import users_db
import cv2
import numpy as np


img = cv2.imread('test.jpg')
img = cv2.resize(img, (600, 400))
_, jpg = cv2.imencode('.jpg', img)

db = users_db.UsersBase('test_db.db')

for i in range(5):
    db.new_user(str(i), str(i), jpg)
    for j in range(10):
        enc = np.random.random((128, 1)).astype(np.float64) + i * 3
        db.add_user_photo(str(i), jpg, enc)

print(db.get_user_encodings('1'))
db.train_new_model()

