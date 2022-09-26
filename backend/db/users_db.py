import datetime
import sqlite3
import logging
from sklearn import neighbors
import pickle

import numpy as np

logger = logging.getLogger('user_db')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('Logs/log_user_db.txt')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class UsersBase:
    def __init__(self, path_to_base='database\\database.db'):
        try:
            logger.info('connecting')
            self.base_connection = sqlite3.connect(path_to_base)
            logger.info('connected')
            self.cursor = self.base_connection.cursor()
            sql_req = 'select sqlite_version();'
            self.cursor.execute(sql_req)
            record = self.cursor.fetchall()
            logger.info('{}'.format(record))
            sql_req = 'CREATE TABLE IF NOT EXISTS users ' \
                      '(' \
                      'id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT DEFAULT 0,' \
                      'name TEXT NOT NULL UNIQUE,' \
                      'card_id TEXT NOT NULL,' \
                      'image BLOB' \
                      ');'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS photos ' \
                      '(' \
                      'id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 0,' \
                      'name TEXT NOT NULL, ' \
                      'date TIMESTAMP NOT NULL,' \
                      'encoding BLOB,' \
                      'image BLOB' \
                      ');'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            sql_req = 'CREATE TABLE IF NOT EXISTS models' \
                      '(' \
                      'id INTEGER PRIMARY KEY AUTOINCREMENT DEFAULT 0,' \
                      'date TIMESTAMP NOT NULL,' \
                      'knn_model BLOB' \
                      ');'
            self.cursor.execute(sql_req)
            self.base_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            logger.exception('Error during connection to database: {}'.format(error))

    def new_user(self, name, card_id, image):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'INSERT OR IGNORE INTO users (name, card_id, image) VALUES (?,?,?);'
            self.cursor.execute(sql_req, (name, card_id, image))
            self.base_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            logger.exception('Error during add new user to database: {}'.format(error))

    def add_user_photo(self, name, image, enc):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'INSERT INTO photos (name, date, image, encoding) VALUES (?,?,?,?);'
            self.cursor.execute(sql_req, (name, datetime.datetime.now(), image.tobytes(), enc.tobytes()))
            self.base_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            logger.exception('Error during add existing user photos to database: {}'.format(error))

    def get_user_face(self, name):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT image FROM users WHERE name=?;'
            self.cursor.execute(sql_req, (name,))
            response = self.cursor.fetchone()
            self.cursor.close()
            face_img = response[0]
            return face_img
        except sqlite3.Error as error:
            logger.exception('Error during fetching face for user {}, {}'.format(name, error))
            return None

    def get_user_names(self):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT name from users;'
            self.cursor.execute(sql_req)
            response = self.cursor.fetchall()
            users = [d[0] for d in response]
            self.base_connection.commit()
            self.cursor.close()
            return users
        except sqlite3.Error as error:
            logger.exception('Error during fetching users: {}'.format(error))
            return None

    def get_card_id(self, name):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT card_id FROM users WHERE name=?;'
            self.cursor.execute(sql_req, (name,))
            response = self.cursor.fetchone()
            self.cursor.close()
            card_id = response[0]
            return card_id
        except sqlite3.Error as error:
            logger.exception('Error during fetching cardID for user {}, {}'.format(name, error))
            return None

    def get_user_photos(self, name):
        try:
            images = []
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT image FROM photos WHERE name=?;'
            self.cursor.execute(sql_req, (name,))
            response = self.cursor.fetchall()
            self.cursor.close()
            for r in response:
                img = np.frombuffer(r[0], dtype=np.uint8)
                img = img.reshape((len(img), 1))
                images.append(img)
            return images
        except sqlite3.Error as error:
            logger.exception('Error during fetching photos for user {}, {}'.format(name, error))
            return None

    def get_user_encodings(self, name):
        try:
            encodings = []
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT encoding FROM photos WHERE name=?;'
            self.cursor.execute(sql_req, (name,))
            response = self.cursor.fetchall()
            self.cursor.close()
            for r in response:
                enc = np.frombuffer(r[0], dtype=np.float64)
                encodings.append(enc.reshape((len(enc))))
            return encodings
        except sqlite3.Error as error:
            logger.exception('Error during fetching encodings for user {}, {}'.format(name, error))
            return None

    def remove_model(self, model_id):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'DELETE FROM models WHERE id=?;'
            self.cursor.execute(sql_req, (model_id,))
            self.base_connection.commit()
            self.cursor.close()
        except sqlite3.Error as error:
            logger.exception('Error during deleting knn model with id={}, {}'.format(model_id, error))

    def train_new_model(self):
        try:
            user_names = self.get_user_names()
            if user_names is None:
                pass
            else:
                train_x = []
                train_y = []
                for user_name in user_names:
                    encodings = self.get_user_encodings(user_name)
                    if encodings is None:
                        continue
                    for enc in encodings:
                        train_x.append(enc)
                        train_y.append(user_name)
                if len(train_x) > 0:
                    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=1, algorithm='ball_tree',
                                                             weights='distance')
                    knn_clf.fit(train_x, train_y)
                    self.cursor = self.base_connection.cursor()
                    sql_req = 'INSERT INTO models (date, knn_model) VALUES (?,?);'
                    self.cursor.execute(sql_req, (datetime.datetime.now(), pickle.dumps(knn_clf)))
                    self.base_connection.commit()
                    self.cursor.close()
                    return True
            return False
        except sqlite3.Error as error:
            logger.exception('Error during training new knn model, {}'.format(error))
            return False

    def get_model(self):
        try:
            self.cursor = self.base_connection.cursor()
            sql_req = 'SELECT knn_model, MAX(date) FROM models;'
            self.cursor.execute(sql_req)
            response = self.cursor.fetchone()
            try:
                knn_model = pickle.loads(response[0])
            except Exception:
                knn_model = None
            self.cursor.close()
            return knn_model
        except sqlite3.Error as error:
            logger.exception('Error during fetching latest knn model {}'.format(error))
            return None

    def close(self):
        if self.base_connection:
            self.base_connection.close()


if __name__ == '__main__':
    pass
