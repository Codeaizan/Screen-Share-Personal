# 🖥️ Remote Desktop Control

A lightweight, web-based remote desktop application that allows screen sharing and remote control over the internet. Built with Python, Flask, Socket.IO, and deployed on Render.

![Remote Desktop](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)

## ✨ Features

- 🌐 **Web-based Remote Access** - No VPN required, works across different networks
- 🎮 **Full Remote Control** - Mouse, keyboard, and scroll control
- 🚀 **Real-time Streaming** - Low latency screen sharing (up to 60 FPS)
- 🔒 **Secure** - Room-based access with unique links, dangerous keys blocked
- 📱 **Cross-platform Viewer** - View from any device with a web browser
- ⚡ **Lightweight** - Runs as a single executable file
- 🔄 **Auto-reconnect** - Handles network interruptions gracefully

## 🎯 Use Cases

- Remote technical support
- Remote work and presentations
- Accessing your computer from anywhere
- Educational demonstrations
- Team collaboration

## 📋 Requirements

### Server (Render)
- Render account (free tier available)
- GitHub account

### Desktop Client
- Windows 10/11
- 4GB RAM minimum
- Internet connection

### Viewer
- Any modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection

## 🚀 Quick Start

### Option 1: Download Pre-built Executable

1. Download `system32.exe` from [Releases](https://github.com/YOUR_USERNAME/remote-desktop-server/releases)
2. Run the executable (right-click → Run as administrator)
3. Click "Start Sharing" in the browser window
4. Copy and share the generated link with viewers

### Option 2: Build from Source

See [Installation Guide](docs/INSTALLATION.md) for detailed instructions.

## 📖 Documentation

- [Installation Guide](docs/INSTALLATION.md) - Complete setup instructions
- [User Guide](docs/USER_GUIDE.md) - How to use the application
- [Configuration Guide](docs/CONFIGURATION.md) - Customization options
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- [Security](docs/SECURITY.md) - Security considerations

## 🏗️ Architecture

┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Desktop Client │ ◄─────► │  Render Server │ ◄─────► │ Viewer │
│ (Windows) │ │ (Flask/Socket) │ │ (Browser) │
└─────────────────┘ └─────────────────┘ └─────────────────┘
Host PC Signal Server Remote User


### Components

1. **Desktop Client** - Python application that captures screen and receives control commands
2. **Render Server** - Flask server handling WebSocket connections and routing
3. **Web Viewer** - Browser-based interface for viewing and controlling the remote screen

## ⚙️ Configuration

Edit these values in `desktop_client.py` to customize performance:

Screen resolution (lower = faster)
SCREEN_WIDTH = 854 # Options: 640, 854, 1280, 1920
SCREEN_HEIGHT = 480 # Options: 360, 480, 720, 1080

JPEG quality (lower = faster, higher = clearer)
JPEG_QUALITY = 35 # Range: 20-95

Frames per second (higher = smoother)
FPS = 45 # Options: 15, 24, 30, 45, 60


## 🛡️ Security Features

- ✅ Unique room IDs for each session
- ✅ Dangerous system keys blocked (Ctrl, Alt, Win)
- ✅ No persistent connections or data storage
- ✅ HTTPS encryption (via Render)
- ✅ Temporary sessions (auto-cleanup on disconnect)

## 🔧 Performance Tips

### For Faster Performance

SCREEN_WIDTH = 640
SCREEN_HEIGHT = 360
JPEG_QUALITY = 30
FPS = 60

### For Better Quality

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
JPEG_QUALITY = 80
FPS = 24


### Balanced (Recommended)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
JPEG_QUALITY = 50
FPS = 30


## 📦 Tech Stack

### Backend
- **Flask** - Web framework
- **Flask-SocketIO** - WebSocket support
- **Python-SocketIO** - Socket.IO Python client
- **Gunicorn** - Production WSGI server

### Frontend
- **Socket.IO Client** - Real-time communication
- **HTML/CSS/JavaScript** - Web interface

### Desktop Client
- **MSS** - Screen capture
- **Pillow** - Image processing
- **PyAutoGUI** - Mouse/keyboard control
- **PyInstaller** - Executable creation

### Deployment
- **Render** - Cloud hosting platform
- **Git** - Version control

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is for legitimate remote access purposes only. Users are responsible for:
- Obtaining proper authorization before accessing remote systems
- Complying with local laws and regulations
- Protecting shared links and access credentials
- Using the software responsibly and ethically

## 🐛 Known Issues

- Windows Defender may flag the executable (false positive)
- Some antivirus software may block remote control features
- High FPS settings may cause lag on slower networks

See [Troubleshooting Guide](docs/TROUBLESHOOTING.md) for solutions.

## 📧 Support

- Create an issue for bug reports
- Start a discussion for questions
- Check documentation for common problems

## 🙏 Acknowledgments

- Flask and Socket.IO communities
- Render platform for free hosting
- All contributors and users

## 📊 Project Status

- ✅ Core functionality complete
- ✅ Remote control working
- ✅ Auto-reconnect implemented
- 🚧 File transfer (planned)
- 🚧 Multi-monitor support (planned)
- 🚧 Mobile app viewer (planned)

---

**Made with ❤️ by [Your Name]**

⭐ Star this repository if you find it useful!
