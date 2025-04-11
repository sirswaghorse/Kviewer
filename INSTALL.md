# Installation Guide for KitelyView v0.1.0

This guide will help you install and run KitelyView on your platform.

## System Requirements

- Python 3.8 or higher
- Operating System: Windows 10+, Ubuntu 20.04+, or Fedora 34+
- Graphics: OpenGL 3.3+ compatible GPU for the desktop version

## Installation Steps

### Step 1: Download the Release

Download the latest release from GitHub:
- Visit: https://github.com/sirswaghorse/Kviewer/releases
- Download the zip file for your platform (or clone the repository)

### Step 2: Extract Files

Extract the zip file to your desired location.

### Step 3: Install Dependencies

Open a terminal/command prompt in the extracted folder and run:

```bash
# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install required packages
pip install -r dependencies.txt
```

### Step 4: Run KitelyView

#### For the Web Version (Recommended for first-time users)

```bash
python web_demo.py
```

Then open your browser and navigate to `http://localhost:5000`

#### For the Desktop Version

```bash
python main.py
```

## Usage Guide

### Login to Kitely

1. Click the "Login to Kitely" button in the left sidebar
2. Enter your Kitely credentials (First Name, Last Name, and Password)
3. Click the login button

### Navigation Controls

- WASD: Move avatar forward, left, backward, right
- QE: Move up/down
- Mouse: Look around
- Space: Jump

### Troubleshooting

If you encounter issues:

1. Ensure all dependencies are installed correctly
2. Check that your system meets the minimum requirements
3. Look for error messages in the terminal/command prompt
4. For web version, ensure port 5000 is not being used by another application

## Additional Resources

- [Kitely Website](https://www.kitely.com/)
- [OpenSimulator Documentation](http://opensimulator.org/wiki/Main_Page)

## License

See the LICENSE file for details.