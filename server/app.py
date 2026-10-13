from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
CORS(app)

# SocketIO configuration
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    ping_timeout=120,
    ping_interval=25,
    max_http_buffer_size=10000000
)

# Store active rooms
active_rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view/<room_id>')
def viewer(room_id):
    return render_template('viewer.html', room_id=room_id)

@app.route('/health')
def health():
    return {'status': 'ok', 'active_rooms': len(active_rooms)}

@socketio.on('connect')
def handle_connect():
    print(f'✅ Client connected: {request.sid}')
    emit('connected', {'status': 'success', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'❌ Client disconnected: {request.sid}')
    for room_id in list(active_rooms.keys()):
        if request.sid in active_rooms.get(room_id, {}).get('viewers', []):
            active_rooms[room_id]['viewers'].remove(request.sid)
        if active_rooms.get(room_id, {}).get('host') == request.sid:
            print(f'🗑️ Removing room {room_id}')
            del active_rooms[room_id]

@socketio.on('create_room')
def handle_create_room(data):
    room_id = data.get('room_id')
    join_room(room_id)
    active_rooms[room_id] = {
        'host': request.sid,
        'viewers': []
    }
    print(f'📺 Room created: {room_id} by {request.sid}')
    emit('room_created', {'room_id': room_id, 'sid': request.sid})

@socketio.on('join_room')
def handle_join_room(data):
    room_id = data.get('room_id')
    join_room(room_id)
    
    if room_id in active_rooms:
        if request.sid not in active_rooms[room_id]['viewers']:
            active_rooms[room_id]['viewers'].append(request.sid)
    else:
        print(f'⚠️ Room {room_id} does not exist')
    
    print(f'👀 Viewer {request.sid} joined room: {room_id}')
    emit('joined_room', {'room_id': room_id, 'sid': request.sid})

@socketio.on('leave_room')
def handle_leave_room(data):
    room_id = data.get('room_id')
    leave_room(room_id)
    
    if room_id in active_rooms and request.sid in active_rooms[room_id].get('viewers', []):
        active_rooms[room_id]['viewers'].remove(request.sid)
    
    print(f'👋 Viewer {request.sid} left room: {room_id}')

@socketio.on('screen_frame')
def handle_screen_frame(data):
    room_id = data.get('room_id')
    frame = data.get('frame')
    
    if room_id in active_rooms:
        emit('screen_update', 
             {'frame': frame}, 
             room=room_id,
             include_self=False)

@socketio.on('control_mouse_move')
def handle_mouse_move(data):
    room_id = data.get('room_id')
    
    if room_id in active_rooms:
        host_sid = active_rooms[room_id]['host']
        emit('control_mouse_move', {
            'x': data.get('x'),
            'y': data.get('y'),
            'screen_width': data.get('screen_width'),
            'screen_height': data.get('screen_height')
        }, to=host_sid)

@socketio.on('control_mouse_click')
def handle_mouse_click(data):
    room_id = data.get('room_id')
    
    if room_id in active_rooms:
        host_sid = active_rooms[room_id]['host']
        emit('control_mouse_click', {
            'button': data.get('button'),
            'type': data.get('type')
        }, to=host_sid)

@socketio.on('control_mouse_scroll')
def handle_mouse_scroll(data):
    room_id = data.get('room_id')
    
    if room_id in active_rooms:
        host_sid = active_rooms[room_id]['host']
        emit('control_mouse_scroll', {
            'delta': data.get('delta')
        }, to=host_sid)

@socketio.on('control_key_press')
def handle_key_press(data):
    room_id = data.get('room_id')
    
    if room_id in active_rooms:
        host_sid = active_rooms[room_id]['host']
        emit('control_key_press', {
            'key': data.get('key')
        }, to=host_sid)

@socketio.on('ping')
def handle_ping():
    emit('pong')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Server starting on port {port}")
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
