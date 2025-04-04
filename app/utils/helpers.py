"""
Helper functions and utilities for various tasks across the application.
"""

import os
import sys
import uuid
import hashlib
import platform
import tempfile
from pathlib import Path

def get_platform_info():
    """Get information about the current platform"""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.architecture(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
    }

def is_windows():
    """Check if running on Windows"""
    return os.name == "nt"

def is_linux():
    """Check if running on Linux"""
    return os.name == "posix"

def is_fedora():
    """Check if running on Fedora"""
    if not is_linux():
        return False
    try:
        with open("/etc/os-release", "r") as f:
            content = f.read()
            return "ID=fedora" in content
    except:
        return False

def is_ubuntu():
    """Check if running on Ubuntu"""
    if not is_linux():
        return False
    try:
        with open("/etc/os-release", "r") as f:
            content = f.read()
            return "ID=ubuntu" in content
    except:
        return False

def get_temp_dir():
    """Get a unique temporary directory for the application"""
    temp_base = tempfile.gettempdir()
    temp_dir = Path(temp_base) / "kitelyview"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir

def generate_uuid():
    """Generate a random UUID"""
    return str(uuid.uuid4())

def hash_password(password, salt=None):
    """
    Hash a password for secure storage or transmission
    If salt is None, a new random salt is generated
    """
    if salt is None:
        salt = os.urandom(32)  # 32 bytes = 256 bits
    
    # Use PBKDF2 with HMAC-SHA256, 100,000 iterations
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    
    return {
        'salt': salt,
        'key': key
    }

def verify_password(stored_password, provided_password):
    """Verify a password against a stored hash"""
    new_key = hashlib.pbkdf2_hmac(
        'sha256',
        provided_password.encode('utf-8'),
        stored_password['salt'],
        100000
    )
    
    return new_key == stored_password['key']

def format_bytes(size):
    """Format byte count as a human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024 or unit == 'TB':
            break
        size /= 1024.0
    return f"{size:.2f} {unit}"

def parse_bytes(size_str):
    """Parse a human-readable byte string to int"""
    units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
    
    size_str = size_str.upper().replace(' ', '')
    if not any(unit in size_str for unit in units):
        try:
            return int(size_str)
        except ValueError:
            return 0
    
    for unit in units:
        if size_str.endswith(unit):
            try:
                number = float(size_str[:-len(unit)])
                return int(number * units[unit])
            except ValueError:
                return 0
    return 0

def create_directory_if_not_exists(directory):
    """Create a directory if it doesn't exist"""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")
        return False
