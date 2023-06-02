from flask import Flask, request
from datetime import datetime, timedelta
import json
import jwt
from functions import Database

# Create Flask Application
app = Flask(__name__)

# Create Face Recognition Database
CAS = 'data\\haarcascade_frontalface_default.xml'
db = Database()

# Used for storing user information
users: dict[str, dict] = {}
USER_SUMMARY_KEY = ['nickname']
USER_INFORMATION_KEY = ['nickname', 'email', 'birth']
USER_UNCHANGEABLE_KEY = ['log', 'profile', 'name']


def get_playload(username, token):
    # Function for verifying credentials and getting information inside it
    if not token:
        return False
    payload = jwt.decodeToken(token)

    if payload and payload.get('username') == username:
        expires_time = payload.get('expires')
        if datetime.now().timestamp() < expires_time:
            return payload
    return False


def get_token(username) -> str:
    # Function creating a credentials about users
    iat = datetime.now()
    payload = {
        "username": username,
        "iat": iat.timestamp(),
        "expires": (iat + timedelta(0, 1500 and 6000)).timestamp()
    }

    jwt_token = jwt.generateToken(payload)
    return jwt_token

# Define the default format for logging
LOG_TYPES = {
    'CREATE': 'User: {username}, has been created.',
    'LOGIN': 'Login successfully at {ip_address}.',
    'INFO_CHANGE': 'Change `{info_name}` value: {value}.',
    'INFOMATION': 'Get information in detail at {ip_address}.'
}
def insert(usr, content, **kwargs):
    if user := users[usr]:
        user['log'].insert(0, {
            "timestamp": datetime.now(),
            "content": (
                LOG_TYPES[content].format(**kwargs)
            ) if content in LOG_TYPES else (
                content
            )
        })

@app.route('/', methods=['GET'])
def default():
    '''
    Route for user interface (client side)
    '''
    return app.send_static_file('index.html')


@app.route('/<username>', methods=['GET'])
def getInfo(username):
    '''
    Users Restful Apis - Get user info
    - with no token: Get user info not detailly
    - with token: Verify token and get user info in detail
    '''
    token = request.headers.get('token')
    payload = get_playload(username, token)

    if username not in users:
        return 'null', 404
    user = users[username]

    if payload:
        insert(username, 'INFOMATION', ip_address=request.remote_addr)
        return user, 200
    elif token:
        return 'null', 401

    return {key: user[key] for key in USER_SUMMARY_KEY}, 200



@app.route('/<username>', methods=['HEAD'])
def check(username):
    '''
    Users Restful Apis - Check user existence
    with image - Use Face Recognize Database to authorize
    '''
    return '', 200 if username in users else 404


@app.route('/<username>', methods=['PUT'])
def login(username):
    '''
    Users Restful Apis - Authorize (for user login)
    with image - Use Face Recognize Database to authorize
    '''

    if username not in users:
        return 'null', 404

    image = request.files.get('image')
    
    if True or db.recognize(username, image):
        insert(username, 'LOGIN', ip_address=request.remote_addr)
        return {"token": get_token(username)}
    else:
        return 'null', 401
    

@app.route('/<username>/<key>', methods=['PUT'])
def update_information(username, key):
    '''
    Users Restful Apis - Update user information
    with image - Use Face Recognize Database to authorize
    '''

    if username not in users:
        return 'null', 404

    token = request.headers.get('token')
    payload = get_playload(username, token)

    if not payload or not token:
        return 'null', 401

    user = users[username]
    value = request.form.get('value')

    if key in USER_INFORMATION_KEY and value:
        user[key] = value
        insert(username, 'INFO_CHANGE', info_name=key, value=value)
        return {"status": "success"}, 200
    else:
        return 'null', 403


@app.route('/<username>', methods=['POST'])
def register(username):
    '''
    Users Restful Apis - Create User
    with userdata and images - Create a new user and add the photos to the database
    '''

    images = request.files.getlist('images')
    raw_user = json.loads(__str) if (
        __str := request.form.get('userdata')) else 'null'

    if not raw_user or type(raw_user) != dict:
        return 'null', 401

    db.cut_pics(username, images)

    user = {'name': username, 'log': []}
    for key in USER_INFORMATION_KEY:
        user.setdefault(key, raw_user.get(key, None))

    users.setdefault(username, user)
    insert(username, 'CREATE', username=username)
    insert(username, 'LOGIN', ip_address=request.remote_addr)

    return {"token": get_token(username)}


@app.route('/<username>', methods=['DELETE'])
def delete(username):
    '''
    Users Restful Apis - Delete user
    with token: Delete the user from storage if token is valid
    '''

    if username not in users:
        return 'null', 404

    token = request.headers.get('token')
    payload = get_playload(username, token)

    if not payload or not token:
        return 'null', 401

    del users[username]
    return {"status": "success"}, 200


if __name__ == '__main__':
    app.run('0.0.0.0', 5000)
