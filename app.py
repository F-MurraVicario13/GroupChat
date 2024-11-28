from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app)

connected_users = {}

@app.route('/')
def index():
    if 'username' not in session:
        return render_template('login.html')
    return render_template('chat.html', username=session['username'])

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    if username:
        session['username'] = username
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return jsonify({'success': True})

@socketio.on('connect')
def handle_connect():
    if 'username' in session:
        connected_users[request.sid] = session['username']
        emit('user_joined', {'username': session['username']}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in connected_users:
        username = connected_users[request.sid]
        emit('user_left', {'username': username}, broadcast=True)
        del connected_users[request.sid]

@socketio.on('send_message')
def handle_message(data):
    if 'username' in session:
        emit('new_message', {
            'username': session['username'],
            'message': data['message']
        }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=7632, debug=True)
