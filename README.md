# KitelyView

KitelyView is a cross-platform OpenSimulator viewer application designed specifically for connecting to the Kitely grid. It provides a streamlined interface for exploring virtual worlds, chatting with other users, managing inventory, and interacting with the 3D environment.

## Features

- **Cross-platform compatibility**: Works on Windows, Fedora, and Ubuntu
- **3D Rendering**: OpenGL-based rendering engine for the virtual world
- **Network Communication**: Connect to OpenSimulator grids using the standard protocol
- **User Interface**: Modern, intuitive interface built with PyQt5
- **Inventory Management**: View and organize your virtual items
- **Chat System**: Communicate with other users in the virtual world
- **Avatar Control**: Move and animate your avatar in the world
- **Object Manipulation**: Create, edit, and interact with virtual objects

## Project Structure

The project is organized into several modules:

- **app/models/**: Data models representing objects in the virtual world
- **app/network/**: Network communication with OpenSimulator servers
- **app/renderer/**: 3D rendering using OpenGL
- **app/ui/**: User interface components
- **app/utils/**: Utility functions and helpers
- **app/assets/**: Application resources (icons, shaders, etc.)

## Dependencies

- Python 3.6+
- PyQt5
- NumPy
- PyOpenGL
- Pillow (PIL)
- requests
- websocket-client

## Installation

1. Clone the repository
2. Install the dependencies:
   ```
   pip install pyqt5 numpy pyopengl pillow requests websocket-client
   ```
3. Run the application:
   ```
   python main.py
   ```

## Demo Mode

To experience a simplified demonstration of the application functionality:

```
python demo.py
```

The demo mode simulates a login to the Kitely grid, teleporting to a region, and sending chat messages without requiring an actual grid connection.

## Configuration

The application uses a configuration file located at `.config/config.json`. For a list of available configuration options, see `app/config.py`.

## How It Works

1. **Login**: Connect to the Kitely grid using your credentials
2. **Region Selection**: Choose a region to visit
3. **Navigation**: Move your avatar around the virtual world
4. **Interaction**: Chat with other users, manipulate objects, access your inventory

## Development

The code is structured to allow easy extension and modification. Key components:

- **OpenSimulator Protocol**: Implementation of the network protocol
- **3D Rendering Engine**: OpenGL-based engine for rendering the virtual world
- **UI Components**: PyQt5 widgets for the application interface

## Contributing

Contributions are welcome! Areas that could use improvement:

- Additional UI features
- Performance optimizations
- Enhanced rendering capabilities
- More comprehensive support for OpenSimulator features

## License

This project is open source under the MIT License.

## Credits

Developed by the KitelyView Team.