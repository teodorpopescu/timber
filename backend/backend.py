import http.client
import json
import os

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

# === Constants loaded from configs ===
USERNAME_MIN_SIZE = config_json["username"]["min_size"]
USERNAME_MAX_SIZE = config_json["username"]["max_size"]
USERNAME_ALLOWED_CHARS = config_json["username"]["allowed_chars"]
PASSWORD_MIN_SIZE = config_json["password"]["min_size"]
PASSWORD_MAX_SIZE = config_json["password"]["max_size"]
PASSWORD_ALLOWED_CHARS = config_json["password"]["allowed_chars"]

# === Constants related to the database queries ===
DB_GET_ALL = "SELECT * FROM Users"
DB_GET_USER = "SELECT * FROM Users WHERE Username = %s"
DB_GET_USERS_BY_AGE = "SELECT * FROM Users WHERE Age > %s AND Age < %s AND Sex = %s"
DB_CREATE_USER = "INSERT INTO Users (Username, FirstName, LastName, Age, Sex) VALUES (%s, %s, %s, %s, %s)"
DB_UPDATE_USER = "UPDATE Users SET FirstName = %s, LastName = %s, Age = %s, Sex = %s WHERE Username = %s"
DB_DELETE_USER = "DELETE FROM Users WHERE Username = %s"

authenticator_client = http.client.HTTPConnection(config_json["authenticator"]["endpoint"])


def is_username_valid(username):
    if len(username) < USERNAME_MIN_SIZE:
        return False
    if len(username) > USERNAME_MAX_SIZE:
        return False
    for c in username:
        if c not in USERNAME_ALLOWED_CHARS:
            return False
    return True


def is_name_valid(name):
    if name is None:
        return False
    for c in name.lower():
        if c not in "abcdefghijklmnopqrstuvwxyz":
            return False
    return True


def is_sex_valid(sex):
    if sex is None:
        return False
    if sex == 'M' or sex == 'F':
        return True
    return False


def is_age_valid(age):
    try:
        age_int = int(age)
        if age_int < 18 or age_int > 120:
            return False
        return True
    except Exception as e:
        return False


def check_authorized(auth_client, username, token):
    headers = {'username': username, 'token': token}
    auth_client.request("GET", "/checkToken", headers=headers)
    response = auth_client.getresponse()
    if response.status < 400:
        return True
    return False


def get_user(username):
    cursor = db_connection.cursor()
    cursor.execute(DB_GET_USER, username)
    user_data = cursor.fetchone()
    if user_data is None:
        return None
    return {
        'firstname': user_data[1],
        'lastname': user_data[2],
        'age': user_data[3],
        'sex': user_data[4]
    }


def create_user(username, firstname, lastname, age, sex):
    cursor = db_connection.cursor()
    cursor.execute(DB_CREATE_USER, (username, firstname, lastname, age, sex))


def update_user(username, firstname, lastname, age, sex):
    cursor = db_connection.cursor()
    cursor.execute(DB_UPDATE_USER, (firstname, lastname, age, sex, username))


def delete_user(username):
    cursor = db_connection.cursor()
    cursor.execute(DB_DELETE_USER, username)


@app.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_user():
    try:

        # Validate username and token
        username = request.headers['username']
        token = request.headers['token']
        if username is None or not is_username_valid(username):
            return Response(status=400, response='Invalid username')
        user_data = get_user(username)
        if not check_authorized(authenticator_client, username, token):
            return Response(status=401, response='Bad username or token')

        if request.method == "POST":
            if user_data is not None:
                return Response(status=403, response='User already exists')
            firstname = request.form['firstname'] if 'firstname' in request.form else None
            lastname = request.form['lastname'] if 'lastname' in request.form else None
            age = request.form['age'] if 'age' in request.form else None
            sex = request.form['sex'] if 'sex' in request.form else None
            if not is_name_valid(firstname):
                return Response(status=400, response="Invalid firstname")
            if not is_name_valid(lastname):
                return Response(status=400, response="Invalid lastname")
            if not is_age_valid(age):
                return Response(status=400, response="Invalid age")
            if not is_sex_valid(sex):
                return Response(status=400, response="Invalid sex")
            create_user(username, firstname, lastname, int(age), sex)
            return Response(status=201, response='User created')

        if user_data is None:
            return Response(status=403, response='User missing')

        # From this point onwards the user exists and it's authenticated
        if request.method == "GET":
            return Response(status=200, response=json.dumps(user_data))
        elif request.method == "PUT":
            firstname = request.form['firstname'] if 'firstname' in request.form else user_data['firstname']
            lastname = request.form['lastname'] if 'lastname' in request.form else user_data['lastname']
            age = request.form['age'] if 'age' in request.form else user_data['age']
            sex = request.form['sex'] if 'sex' in request.form else user_data['sex']
            if not is_name_valid(firstname):
                return Response(status=400, response="Invalid firstname")
            if not is_name_valid(lastname):
                return Response(status=400, response="Invalid lastname")
            if not is_age_valid(age):
                return Response(status=400, response="Invalid age")
            if not is_sex_valid(sex):
                return Response(status=400, response="Invalid sex")
            update_user(username, firstname, lastname, int(age), sex)
            return Response(status=201, response='User updated')
        elif request.method == "DELETE":
            delete_user(username)
            return Response(status=200, response="User deleted")
        else:
            return Response(status=500, response="Invalid method")
    except Exception as e:
        return Response(status=500, response=str(e))


@app.route('/findMatch', methods=['GET'])
def find_match():
    try:
        # Validate username and token
        username = request.headers['username']
        token = request.headers['token']
        if username is None or not is_username_valid(username):
            return Response(status=400, response='Invalid username')
        user_data = get_user(username)
        if not check_authorized(authenticator_client, username, token):
            return Response(status=401, response='Bad username or token')

        desired_sex = 'F' if user_data['sex'] == 'M' else 'M'
        older_than = request.form['olderThan'] if 'olderThan' in request.form else 18
        younger_than = request.form['youngerThan'] if 'youngerThan' in request.form else 120
        if not (is_age_valid(older_than) and is_age_valid(younger_than)):
            return Response(status=400, response="Invalid ages")
        cursor = db_connection.cursor();
        cursor.execute(DB_GET_USERS_BY_AGE, (older_than, younger_than, desired_sex))
        return Response(status=200, response=json.dumps(cursor.fetchall()))
    except Exception as e:
        return Response(status=500, response=str(e))


@app.route('/everything', methods=['GET'])
def get_everything():
    cursor = db_connection.cursor()
    cursor.execute(DB_GET_ALL)
    return Response(status=200, response=json.dumps(cursor.fetchall()))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
