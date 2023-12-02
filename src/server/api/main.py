from flask import Flask, jsonify, request, session

from src.server import DataCollector, face_matching_probability


app = Flask(__name__)


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    try:
        DataCollector(username, password)
    except Exception as e:
        return jsonify({'message': 'Failed to login', 'error': e}), 401

    session['username'] = username
    session['password'] = password

    return jsonify({'message': 'Login successful'}), 200
