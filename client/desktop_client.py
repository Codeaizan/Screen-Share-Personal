import mss
from PIL import Image
import io
import base64
import threading
import time
import socketio
import pyautogui
import webbrowser
from flask import Flask, render_template_string

# ==================== CONFIGURATION ====================
# YOUR RAILWAY URL - Change this to your actual Railway deployment URL
SERVER_URL = "https://web-production-6f5f6.up.railway.app"

# Local Flask server port for control panel
PORT = 8080

# Disable PyAutoGUI fail-safe (allows mouse to go to corners)
pyautogui.FAILSAFE = False

# ==================== SCREEN SHARING SETTINGS ====================
# Resolution settings - Smaller = Faster, Larger = Better quality
# Options: (854, 480), (960, 540), (1280, 720), (1920, 1080)
SCREEN_WIDTH = 854   # Width in pixels
SCREEN_HEIGHT = 480  # Height in pixels

# JPEG quality - Lower = Faster but blurry, Higher = Slower but clear
# Range: 1-100 (Recommended: 30-80)
JPEG_QUALITY = 70    # Current: 35 (fastest)

# Frames per second - Higher = Smoother but uses more bandwidth
# Options: 15, 24, 30, 45, 60
FPS = 45             # Current: 45 FPS (very smooth)

# ==================== FLASK APP ====================
app = Flask(__name__)
sio = socketio.Client(logger=False, engineio_logger=False)

# Global state variables
is_sharing = False
screen_thread = None
room_id = None
share_link = None

# ==================== HTML CONTROL PANEL ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Remote Desktop Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        button {
            padding: 15px 40px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px;
            width: 200px;
            font-weight: bold;
        }
        .start-btn {
            background: #4CAF50;
            color: white;
        }
        .start-btn:hover {
            background: #45a049;
        }
        .stop-btn {
            background: #f44336;
            color: white;
        }
        .stop-btn:hover {
            background: #da190b;
        }
        .status {
            text-align: center;
            margin: 20px 0;
            font-weight: bold;
            font-size: 18px;
            padding: 15px;
            border-radius: 5px;
            background: #f5f5f5;
        }
        .status.active {
            background: #4CAF50;
            color: white;
        }
        .link-box {
            background: #e3f2fd;
            padding: 20px;
            border-radius: 5px;
            margin-top: 20px;
            display: none;
        }
        .link-box.show {
            display: block;
        }
        .link-input {
            width: 100%;
            padding: 12px;
            font-size: 14px;
            border: 2px solid #2196F3;
            border-radius: 4px;
            margin: 10px 0;
            box-sizing: border-box;
        }
        .copy-btn {
            background: #2196F3;
            color: white;
            padding: 12px 30px;
            width: auto;
        }
        .copy-btn:hover {
            background: #0b7dda;
        }
        .info {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
        }
        .button-group {
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ Remote Desktop Control</h1>
        <p class="subtitle">Share and control your screen remotely</p>
        
        <div class="status" id="status">Not Sharing</div>
        
        <div class="button-group">
            <button class="start-btn" onclick="startSharing()">Start Sharing</button>
            <button class="stop-btn" onclick="stopSharing()">Stop Sharing</button>
        </div>
        
        <div class="link-box" id="linkBox">
            <h3>📤 Share this link with viewers:</h3>
            <input type="text" class="link-input" id="shareLink" readonly>
            <button class="copy-btn" onclick="copyLink()">Copy Link</button>
            <p style="margin-top: 15px; color: #666;">
                <strong>Note:</strong> Viewers can see and control your screen using this link
            </p>
        </div>

        <div class="info">
            <strong>⚠️ Privacy Notice:</strong> Your screen will be visible and controllable by anyone with the link. 
            Only share with trusted people.
        </div>
    </div>

    <script>
        async function startSharing() {
            try {
                const res = await fetch('/start');
                const data = await res.json();
                if (data.status === 'started') {
                    document.getElementById('status').textContent = '🟢 Sharing Active';
                    document.getElementById('status').classList.add('active');
                    document.getElementById('linkBox').classList.add('show');
                    document.getElementById('shareLink').value = data.link;
                } else if (data.status === 'error') {
                    alert('Error: ' + data.message);
                    document.getElementById('status').textContent = '❌ Error';
                }
            } catch (e) {
                alert('Failed to start: ' + e);
            }
        }

        async function stopSharing() {
            await fetch('/stop');
            document.getElementById('status').textContent = 'Not Sharing';
            document.getElementById('status').classList.remove('active');
            document.getElementById('linkBox').classList.remove('show');
        }

        function copyLink() {
            const input = document.getElementById('shareLink');
            input.select();
            document.execCommand('copy');
            alert('✅ Link copied to clipboard!');
        }
    </script>
</body>
</html>
"""

# ==================== SCREEN CAPTURE FUNCTION ====================
def capture_and_send_screen():
    """
    Captures screen continuously and sends to server
    Includes auto-reconnect if connection drops
    """
    global is_sharing, room_id
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # Primary monitor (0 = all monitors, 1 = primary)
        
        while is_sharing:
            try:
                # Auto-reconnect if disconnected
                if not sio.connected:
                    try:
                        sio.connect(SERVER_URL, wait_timeout=10, transports=['websocket', 'polling'])
                        time.sleep(0.5)
                        sio.emit('create_room', {'room_id': room_id})
                        time.sleep(1)
                    except:
                        time.sleep(2)  # Wait before retry
                        continue
                
                # Capture screenshot
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Resize image - MODIFY SCREEN_WIDTH and SCREEN_HEIGHT at top
                # Smaller = Faster, Larger = Better quality
                img.thumbnail((SCREEN_WIDTH, SCREEN_HEIGHT), Image.Resampling.LANCZOS)
                
                # Convert to JPEG and compress
                buffer = io.BytesIO()
                # JPEG_QUALITY: 1-100 (Lower = Faster, Higher = Better quality)
                img.save(buffer, format='JPEG', quality=JPEG_QUALITY)
                
                # Encode to base64 for transmission
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                # Send frame to server
                sio.emit('screen_frame', {
                    'room_id': room_id,
                    'frame': img_str
                })
                
                # FPS control - MODIFY FPS variable at top
                # time.sleep(1/FPS) where FPS = frames per second
                # Examples: 15 FPS = 1/15, 30 FPS = 1/30, 60 FPS = 1/60
                time.sleep(1/FPS)
                
            except:
                time.sleep(1)  # Error handling - wait and retry

# ==================== SOCKET.IO EVENT HANDLERS ====================

@sio.on('connect')
def on_connect():
    """Called when connected to server"""
    pass

@sio.on('disconnect')
def on_disconnect():
    """Called when disconnected from server"""
    pass

@sio.on('connected')
def on_connected(data):
    """Server acknowledgment of connection"""
    pass

@sio.on('room_created')
def on_room_created(data):
    """Server acknowledgment of room creation"""
    pass

@sio.on('control_mouse_move')
def on_mouse_move(data):
    """
    Handle mouse movement from viewer
    Converts viewer's screen coordinates to actual screen coordinates
    """
    try:
        x = int(data['x'])
        y = int(data['y'])
        sw = data['screen_width']   # Viewer's screen width
        sh = data['screen_height']  # Viewer's screen height
        
        # Get actual screen dimensions
        actual_w, actual_h = pyautogui.size()
        
        # Scale coordinates from viewer screen to actual screen
        actual_x = int((x / sw) * actual_w)
        actual_y = int((y / sh) * actual_h)
        
        # Ensure coordinates are within screen bounds
        actual_x = max(0, min(actual_x, actual_w - 1))
        actual_y = max(0, min(actual_y, actual_h - 1))
        
        # Move mouse instantly (duration=0 for no animation)
        pyautogui.moveTo(actual_x, actual_y, duration=0)
    except:
        pass

@sio.on('control_mouse_click')
def on_mouse_click(data):
    """
    Handle mouse clicks from viewer
    Supports left, right, middle buttons
    Supports single and double clicks
    """
    try:
        button = data.get('button', 'left')      # left, right, or middle
        click_type = data.get('type', 'single')  # single or double
        
        if click_type == 'double':
            pyautogui.doubleClick(button=button)
        else:
            pyautogui.click(button=button)
    except:
        pass

@sio.on('control_mouse_scroll')
def on_scroll(data):
    """
    Handle mouse scroll from viewer
    Positive delta = scroll up, Negative = scroll down
    Multiplier controls scroll speed (currently 3x)
    """
    try:
        delta = data['delta']
        # Scroll multiplier - MODIFY to change scroll speed
        # Higher = Faster scroll (try 1, 3, 5, 10)
        pyautogui.scroll(delta * 3)
    except:
        pass

@sio.on('control_key_press')
def on_key_press(data):
    """
    Handle keyboard input from viewer
    SECURITY: Blocks dangerous keys (Ctrl, Alt, Windows key)
    """
    try:
        key = data['key']
        
        # SECURITY: Block dangerous system keys
        # These keys can trigger system shortcuts or security issues
        blocked_keys = ['Control', 'Alt', 'Meta', 'OS', 'Win']
        if key in blocked_keys:
            return  # Ignore blocked keys
        
        # Map special keys to PyAutoGUI key names
        special_keys = {
            'Enter': 'enter',
            'Backspace': 'backspace',
            'Tab': 'tab',
            'Escape': 'esc',
            'Delete': 'delete',
            'ArrowUp': 'up',
            'ArrowDown': 'down',
            'ArrowLeft': 'left',
            'ArrowRight': 'right',
            ' ': 'space',
            'Home': 'home',
            'End': 'end',
            'PageUp': 'pageup',
            'PageDown': 'pagedown'
        }
        
        # Press the key
        if key in special_keys:
            pyautogui.press(special_keys[key])
        elif len(key) == 1:
            pyautogui.press(key.lower())
    except:
        pass

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    """Main control panel page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/start')
def start():
    """Start screen sharing"""
    global is_sharing, screen_thread, room_id, share_link
    
    if not is_sharing:
        try:
            # Connect to Railway server
            sio.connect(SERVER_URL, wait_timeout=10, transports=['websocket', 'polling'])
            time.sleep(1)
            
            # Create unique room ID (timestamp)
            room_id = str(int(time.time()))
            sio.emit('create_room', {'room_id': room_id})
            time.sleep(0.5)
            
            # Start screen capture thread
            is_sharing = True
            screen_thread = threading.Thread(target=capture_and_send_screen, daemon=True)
            screen_thread.start()
            
            # Generate viewer link
            share_link = f"{SERVER_URL}/view/{room_id}"
            
            return {'status': 'started', 'link': share_link}
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    return {'status': 'already_running', 'link': share_link}

@app.route('/stop')
def stop():
    """Stop screen sharing"""
    global is_sharing
    is_sharing = False
    if sio.connected:
        sio.disconnect()
    return {'status': 'stopped'}

# ==================== AUTO-OPEN BROWSER ====================
def open_browser():
    """Opens control panel in browser automatically"""
    time.sleep(1.5)
    webbrowser.open(f'http://localhost:{PORT}')

# ==================== MAIN ENTRY POINT ====================
if __name__ == '__main__':
    # Start browser in background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Flask server
    app.run(host='localhost', port=PORT, debug=False)
