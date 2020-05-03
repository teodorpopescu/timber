import json
import os
import requests

def load_json_from_file(dir, file):
    file_path = os.path.join(dir, file)
    with open(file_path, 'r') as f:
        content = json.loads(f.read())
    return content

config_json = load_json_from_file(".", "config.json")
AUTHENTICATOR = config_json["authenticator_endpoint"]
BACKEND = config_json["backend_endpoint"]

AUTH_USER_URL = f'{AUTHENTICATOR}/user'
AUTH_GET_TOKEN_URL = f'{AUTHENTICATOR}/getToken'

BACKEND_USER_URL = f'{BACKEND}/user'
BACKEND_MATCH_URL = f'{BACKEND}/findMatch'

_username = "user"
_password = "password"


def login(username, password):
    global _username
    global _password
    _username = username
    _password = password


def get_token(username, password):
    response = requests.get(AUTH_GET_TOKEN_URL, headers={'username': username, 'password': password})
    # print(f'[Token] Received \'{response.text}\'.')
    response.raise_for_status()
    return response.text


def create_new_user(username, password, firstname, lastname, age, sex):
    response = requests.post(AUTH_USER_URL, headers={'username': username, 'password': password})
    response.raise_for_status()
    token = get_token(username, password)
    response = requests.post(BACKEND_USER_URL, headers={'username': username, 'token': token},
        data={'firstname': firstname, 'lastname': lastname, 'age': int(age), 'sex': sex})
    response.raise_for_status()

def get_matches(olderThan, youngerThan):
    global _username
    global _password
    token = get_token(_username, _password)
    response = requests.get(BACKEND_MATCH_URL, headers={'username': _username, 'token': token},
                            data={'olderThan': olderThan, 'youngerThan': youngerThan})
    response.raise_for_status()
    return response.text


def main():
    while True:
        try:
            print("=======================================================================")
            print("Press: 1 = create profile, 2 = login, 3 = quit")
            key = int(input())
            if key == 1:
                print("CREATING PROFILE...")
                print("Insert username:", end=" ")
                username = input().strip()
                print("Insert password:", end=" ")
                password = input().strip()
                print("Insert first name:", end=" ")
                firstname = input().strip()
                print("Insert last name:", end=" ")
                lastname = input().strip()
                print("Insert age:", end=" ")
                age = input().strip()
                print("Insert sex (M or F):", end=" ")
                sex = input().strip()
                create_new_user(username, password, firstname, lastname, age, sex)
                login(username, password)
                print("LOGGED IN")
            elif key == 2:
                print("LOGING IN...")
                print("Insert username:", end=" ")
                username = input().strip()
                print("Insert password:", end=" ")
                password = input().strip()
                get_token(username, password)
                login(username, password)
                print("LOGGED IN")
            elif key == 3:
                break
            else:
                continue

            while True:
                print("=======================================================================")
                print("Press: 1 = find match, 2 = logout")
                key = int(input())
                if key == 1:
                    print("FINDING MATCH...")
                    print("Insert minimum age:", end=" ")
                    olderThan = input().strip()
                    print("Insert maximum age:", end=" ")
                    youngerThan = input().strip()
                    print("Possible matches are:")
                    for match in json.loads(get_matches(olderThan, youngerThan)):
                        username = match[0]
                        firstname = match[1]
                        lastname = match[2]
                        age = match[3]
                        sex = match[4]
                        print(f'{firstname} {lastname} ({username}), {age} years old')
                elif key == 2:
                    break
                else:
                    continue
        except Exception as e:
            print(f'Error: ${e}')

if __name__ == "__main__":
    main()
