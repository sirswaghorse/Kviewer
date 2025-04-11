# KViewer

A viewer designed for intuitive and engaging virtual world exploration, focusing on user experience and grid interaction, particularly for the Kitely grid.

## Features

- Python-based application with modern UI/UX design
- Qt framework for responsive cross-platform interface
- Web-based interface using Flask, Socket.IO, and Three.js
- Support for Windows, Fedora, and Ubuntu platforms
- Advanced OpenSimulator grid connection protocols
- 3D avatar visualization and customization
- Inventory management system
- Object creation and placement tools
- Chat functionality
- Immersive 3D scene rendering

## Architecture

The application is built with a modular architecture:

- **UI Layer**: Both PyQt5 desktop interface and web-based interface
- **Network Layer**: Handles communication with OpenSimulator grids
- **Renderer**: 3D visualization using OpenGL (desktop) and Three.js (web)
- **Models**: Data structures for avatars, inventory, objects, etc.
- **Utils**: Common utilities and helper functions

## Requirements

- Python 3.8+
- PyQt5 (for desktop version)
- Flask (for web version)
- PyOpenGL
- Pillow
- NumPy
- WebSocket client

## Usage

### Web Version

```
python web_demo.py
```

Access the application at http://localhost:5000

### Desktop Version

```
python main.py
```

## Screenshots

*Coming soon*

## License

*TBD*

## Acknowledgements

This project is designed as a third-party viewer for connecting to OpenSimulator-based virtual worlds, with a focus on the Kitely grid.
