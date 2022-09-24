import argparse
from flask import Flask, render_template, request, Response, jsonify
import logging
from db import users_db
import threading
from utils import utils


DB_PATH = 'db_media/user_base.db'


ap = argparse.ArgumentParser()
ap.add_argument("-p", "--port", required=True, default=5000, type=int,
                help="path to input dataset")
args = vars(ap.parse_args())

logger = logging.getLogger('db_at_port_' + str(args['port']))
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('Logs/log_db_at_port_' + str(args['port']) + '.txt')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

db_lock = threading.Lock()

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/api/add_new', methods=['POST'])
def add_new_request():
    r = request
    img = utils.str2jpeg(r.form['image'])
    card_id = r.form['card_id']
    user_name = r.form['name']

    db_lock.acquire()
    db = users_db.UsersBase(DB_PATH)
    db.new_user(user_name, card_id, img)
    db.close()
    db_lock.release()
    return jsonify({'response': 'ok'})


@app.route('/api/add_photo', methods=['POST'])
def add_photo_request():
    r = request
    img = utils.str2jpeg(r.form['image'])
    enc = utils.str2encoding(r.form['encoding'])
    user_name = r.form['name']

    db_lock.acquire()
    db = users_db.UsersBase(DB_PATH)
    db.add_user_photo(user_name, img, enc)
    db.close()
    db_lock.release()
    return jsonify({'response': 'ok'})


@app.route('/api/get_face', methods=['POST'])
def get_face_request():
    r = request
    user_name = r.form['name']

    db_lock.acquire()
    db = users_db.UsersBase(DB_PATH)
    img = db.get_user_face(user_name)
    db.close()
    db_lock.release()
    json_img = utils.jpeg2str(img)
    return jsonify({'response': 'ok', 'face': json_img})


@app.route('/api/get_names', methods=['POST'])
def get_names_request():
    db_lock.acquire()
    db = users_db.UsersBase(DB_PATH)
    user_names = db.get_user_names()
    db.close()
    db_lock.release()
    return jsonify({'response': 'ok', 'users': user_names})


@app.route('/api/get_card', methods=['POST'])
def get_card_request():
    r = request
    user_name = r.form['name']
    db_lock.acquire()
    db = users_db.UsersBase(DB_PATH)
    card_id = db.get_card_id(user_name)
    db.close()
    db_lock.release()
    return jsonify({'response': 'ok', 'card_id': card_id})


@app.route('/api/rm_model', methods=['POST'])
def rm_model_request():
    r = request
    model_id = r.form['model_id']
    db_lock.acquire()
    db = users_db.UsersBase(DB_PATH)
    db.remove_model(model_id)
    db.close()
    db_lock.release()
    return jsonify({'response': 'ok'})


@app.route('/api/get_model', methods=['POST'])
def get_model_request():
    db_lock.acquire()
    db = users_db.UsersBase(DB_PATH)
    model = db.get_model()
    db.close()
    db_lock.release()
    json_model = utils.model2str(model)
    return jsonify({'response': 'ok', 'model': json_model})


@app.route('/api/train_model', methods=['POST'])
def train_model_request():
    db_lock.acquire()
    db = users_db.UsersBase(DB_PATH)
    db.train_new_model()
    db.close()
    db_lock.release()
    return jsonify({'response': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0')
