from flask import Flask, request, render_template
import requests
import json
import random
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SIGNALWIRE_PROJECT_ID = os.environ['SIGNALWIRE_PROJECT_ID']
SIGNALWIRE_API_TOKEN = os.environ['SIGNALWIRE_API_TOKEN']
SIGNALWIRE_SPACE_URL = os.environ['SIGNALWIRE_SPACE_URL']


# handle HTTP requests
def handle_http(payload, endpoint):
    user = SIGNALWIRE_PROJECT_ID
    passw = SIGNALWIRE_API_TOKEN

    data = json.dumps(payload)
    print(data)

    response = requests.post("https://" + SIGNALWIRE_SPACE_URL + "/api/video/" + endpoint,
                             data=data,
                             auth=HTTPBasicAuth(user, passw),
                             headers={"Content-Type": "application/json"})
    print(response)
    return json.loads(response.text)


# request regular user token
def request_guest_token(room, user=None):
    payload = dict()
    payload['room_name'] = room
    payload['user_name'] = user if user else "user_" + str(random.randint(1111, 9999))
    permissions = ["room.self.audio_mute",
                   "room.self.audio_unmute",
                   "room.self.video_mute",
                   "room.self.video_unmute"]
    payload['permissions'] = permissions
    result = handle_http(payload, 'room_tokens')
    print('Token is: ' + result['token'])
    return result['token']


# request moderator token with privileges to control other users as well
def request_moderator_token(room, user=None):
    payload = dict()
    payload['room_name'] = room
    payload['user_name'] = user if user else str(random.randint(1111, 9999))
    permissions = ["room.self.audio_mute",
                   "room.self.audio_unmute",
                   "room.self.video_mute",
                   "room.self.video_unmute",
                   "room.member.audio_mute",
                   "room.member.audio_unmute",
                   "room.member.video_mute",
                   "room.member.video_unmute",
                   "room.member.remove",
                   ]
    payload['permissions'] = permissions
    result = handle_http(payload, 'room_tokens')
    print('Token is: ' + result['token'])
    return result['token']


# Create a room to join
def create_room(room):
    payload = {
        'name': room,
        'display_name': room,
        'max_participants': 5,
        'delete_on_end': False
    }

    return handle_http(payload, 'rooms')


# assign user with moderator privileges (control other users)
@app.route("/", methods=['GET', "POST"])
def assignMod():
    # set default room for when no custom room is chosen
    defaultRoom = 'Main_Office'
    userType = "Moderator"

    # allow users to assign custom rooms by passing parameter for room through form
    if request.args.get('room'):
        room = request.args.get('room')
    else:
        room = defaultRoom

    # allow users to assign custom user by passing parameter for user through form
    if request.args.get('user'):
        user = request.args.get('user')
    else:
        user = "user_" + str(random.randint(1, 100))

    create_room(room)
    moderatorToken = request_moderator_token(room, user)

    return render_template('mod.html', room=room, user=user, token=moderatorToken, logo='/static/translogo.png', userType=userType)


# assign guest role - no ability to control other users
@app.route("/guest", methods=['GET', "POST"])
def assignGuest():
    # set default room for when no custom room is chosen
    defaultRoom = 'Main_Office'
    userType = "Regular User"

    # allow users to assign custom rooms by passing parameter for room through form
    if request.args.get('room'):
        room = request.args.get('room')
    else:
        room = defaultRoom

    # allow users to assign custom user by passing parameter for user through form
    if request.args.get('user'):
        user = request.args.get('user')
    else:
        user = "user_" + str(random.randint(1, 100))

    create_room(room)
    guestToken = request_guest_token(room, user)

    return render_template('guest.html', room=room, user=user, token=guestToken, logo='/static/translogo.png', userType=userType)


if __name__ == "__main__":
    app.run(debug=True)
