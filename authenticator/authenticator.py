import base64
import hashlib
import json
import os
import time

from Crypto.Cipher import AES
from Crypto import Random
from flask import Flask, request, Response
from flaskext.mysql import MySQL


def load_json_from_file(dir, file):
    file_path = os.path.join(dir, file)
    with open(file_path, 'r') as f:
        content = json.loads(f.read())
    return content


# === Initialize the app and the connection to the database ===
app = Flask(__name__)
mysql = MySQL()
# Configure the database connection according to the given file
config_json = load_json_from_file(".", "config.json")
app.config["MYSQL_DATABASE_HOST"] = config_json["database"]["host"]
app.config["MYSQL_DATABASE_PORT"] = config_json["database"]["port"]
app.config["MYSQL_DATABASE_USER"] = config_json["database"]["user"]
app.config["MYSQL_DATABASE_PASSWORD"] = config_json["database"]["password"]
app.config["MYSQL_DATABASE_DB"] = config_json["database"]["name"]
mysql.init_app(app)
db_connection = mysql.connect()
# For making the operations show the current state of the database
db_connection.autocommit(True)
key = config_json["aes_key"]
token_valid_time = config_json["token_valid_time"]

# === Constants loaded from configs ===
SALT_SIZE = config_json["salt_size"]
USERNAME_MIN_SIZE = config_json["username"]["min_size"]
USERNAME_MAX_SIZE = config_json["username"]["max_size"]
USERNAME_ALLOWED_CHARS = config_json["username"]["allowed_chars"]
PASSWORD_MIN_SIZE = config_json["password"]["min_size"]
PASSWORD_MAX_SIZE = config_json["password"]["max_size"]
PASSWORD_ALLOWED_CHARS = config_json["password"]["allowed_chars"]

# === Constants related to the database queries ===
DB_GET_ALL = "SELECT * FROM Authentication"
DB_GET_USER = "SELECT * FROM Authentication WHERE Username = %s"
DB_CREATE_USER = "INSERT INTO Authentication (Username, Password, Salt) VALUES (%s, %s, %s)"
DB_UPDATE_USER = "UPDATE Authentication SET Password = %s WHERE Username = %s"
DB_DELETE_USER = "DELETE FROM Authentication WHERE Username = %s"


class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


cipher = AESCipher(key)

def generate_salt():
    return Random.get_random_bytes(SALT_SIZE)


def is_username_valid(username):
    if len(username) < USERNAME_MIN_SIZE:
        return False
    if len(username) > USERNAME_MAX_SIZE:
        return False
    for c in username:
        if c not in USERNAME_ALLOWED_CHARS:
            return False
    return True


def is_password_valid(password):
    if len(password) < PASSWORD_MIN_SIZE:
        return False
    if len(password) > PASSWORD_MAX_SIZE:
        return False
    for c in password:
        if c not in PASSWORD_ALLOWED_CHARS:
            return False
    return True


def get_user(username):
    cursor = db_connection.cursor()
    cursor.execute(DB_GET_USER, username)
    user_data = cursor.fetchone()
    if user_data is None:
        return None
    return {
        'username': user_data[0],
        'password_hash_base64': user_data[1],
        'salt_base64': user_data[2]
    }


def check_authorized(username, password, user_data):
    if username != user_data['username']:
        return False
    encoded_salt = user_data['salt_base64'];
    salted_password = password + encoded_salt
    if salted_password == cipher.decrypt(user_data['password_hash_base64']):
        return True
    return False


def generate_token(username):
    time_ms = int(round(time.time() * 1000))
    message = username + '|' + str(time_ms)
    return cipher.encrypt(message)


def verify_token(username, token):
    try:
        time_ms = int(round(time.time() * 1000))
        message = cipher.decrypt(token)
        parts = message.split('|')
        if parts[0] != username:
            return False
        if time_ms - int(parts[1]) > token_valid_time * 1000:
            return False
        return True
    except Exception as e:
        print(str(e), flush=True)
        return False


def create_user(username, password):
    cursor = db_connection.cursor()
    salt = generate_salt()
    encoded_salt = base64.b64encode(salt).decode('utf-8')
    password_hash = cipher.encrypt(password + encoded_salt)
    cursor.execute(DB_CREATE_USER, (username, password_hash, encoded_salt))


def update_user(username, new_password):
    cursor = db_connection.cursor()
    salt = generate_salt()
    encoded_salt = base64.b64encode(salt).decode('utf-8')
    password_hash = cipher.encrypt(new_password + encoded_salt)
    cursor.execute(DB_DELETE_USER, (password_hash, encoded_salt, username))


def delete_user(username):
    cursor = db_connection.cursor()
    cursor.execute(DB_DELETE_USER, username)


@app.route('/user', methods=['POST', 'PUT', 'DELETE'])
def manage_user():
    try:
        # Validate username and password
        username = request.headers['username']
        password = request.headers['password']
        if username is None or not is_username_valid(username):
            return Response(status=400, response='Invalid username')
        if password is None or not is_password_valid(password):
            return Response(status=400, response='Invalid password')
        user_data = get_user(username)

        if request.method == "POST":
            if user_data is not None:
                return Response(status=403, response='User already exists')
            create_user(request.headers['username'], request.headers['password'])
            return Response(status=201, response='User created')
        elif request.method == "PUT":
            if user_data is None:
                return Response(status=403, response="User missing")
            new_password = request.headers['new_password']
            if new_password is None:
                return Response(status=400, response="New password missing")
            if check_authorized(username, password, user_data):
                update_user(username, new_password)
                return Response(status=200, response="Password updated")
            else:
                return Response(status=401, response="Bad username or password")
        elif request.method == "DELETE":
            if user_data is None:
                return Response(status=403, response="User missing")
            if check_authorized(username, password, user_data):
                delete_user(username)
            else:
                return Response(status=401, response="Bad username or password")
            return "Success"
        else:
            return "Invalid method"
    except Exception as e:
        return Response(status=500, response=str(e))


@app.route('/getToken', methods=['GET'])
def get_token():
    try:
        # Validate username and password
        username = request.headers['username']
        password = request.headers['password']
        if username is None or not is_username_valid(username):
            return Response(status=400, response='Invalid username')
        if password is None or not is_password_valid(password):
            return Response(status=400, response='Invalid password')
        user_data = get_user(username)

        if check_authorized(username, password, user_data):
            return Response(status=200, response=generate_token(username))
        else:
            return Response(status=401, response="Bad username or password")
    except Exception as e:
        return Response(status=500, response=str(e))


@app.route('/checkToken', methods=['GET'])
def check_token():
    try:
        # Validate username and password
        username = request.headers['username']
        token = request.headers['token']
        print(token, flush=True)
        if username is None or not is_username_valid(username):
            return Response(status=400, response='Invalid username')
        if token is None:
            return Response(status=401, response='Invalid token')

        if verify_token(username, token):
            return Response(status=200, response='Valid token')
        else:
            return Response(status=401, response="Invalid token")
    except Exception as e:
        return Response(status=500, response=str(e))


@app.route('/everything', methods=['GET'])
def get_everything():
    cursor = db_connection.cursor();
    cursor.execute(DB_GET_ALL)
    return Response(status=200, response=json.dumps(cursor.fetchall()))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
