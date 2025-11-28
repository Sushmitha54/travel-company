import logging
import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set up logging
log_dir = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=os.path.join(log_dir, 'app.log'), level=logging.INFO)

# In-memory storage
users = {}  # username: password
user_dest = {}  # username: {'location': , 'destination': }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    return {'status': 'healthy'}

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if username in users:
        return {'error': 'User exists'}, 400
    users[username] = password
    logging.info(f'User {username} registered')
    return {'message': 'Registered'}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if users.get(username) == password:
        return {'message': 'Logged in'}
    return {'error': 'Invalid credentials'}, 401

@app.route('/destination', methods=['POST'])
def set_destination():
    data = request.get_json()
    username = data.get('username')
    location = data.get('location')
    destination = data.get('destination')
    if username not in users:
        return {'error': 'Not logged in'}, 401
    user_dest[username] = {'location': location, 'destination': destination}
    logging.info(f'User {username} set destination {destination}')
    return {'message': 'Destination set'}

@app.route('/find_companions')
def find_companions():
    # Group users by destination
    from collections import defaultdict
    groups = defaultdict(list)
    for user, info in user_dest.items():
        groups[info['destination']].append({'username': user, 'location': info['location']})
    # Only show groups with more than 1 person
    result = {dest: group for dest, group in groups.items() if len(group) > 1}
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
