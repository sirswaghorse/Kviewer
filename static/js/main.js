/**
 * KitelyView - Main Application Script
 * Coordinates all modules and handles communication with the server
 */

// Global function to add log entries (used by multiple modules)
function addLogEntry(message, level) {
    const systemLog = document.getElementById('system-log');
    if (!systemLog) return;
    
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${level}`;
    logEntry.textContent = message;
    
    systemLog.appendChild(logEntry);
    
    // Auto-scroll to bottom
    systemLog.scrollTop = systemLog.scrollHeight;
}

document.addEventListener('DOMContentLoaded', function() {
    // UI Elements
    const startButton = document.getElementById('start-button');
    const statusIndicator = document.getElementById('status-indicator');
    const loginStatus = document.getElementById('login-status');
    const loginButton = document.getElementById('login-button');
    const logoutButton = document.getElementById('logout-button');
    const userName = document.getElementById('user-name');
    const userId = document.getElementById('user-id');
    const regionName = document.getElementById('region-name');
    const regionPosition = document.getElementById('region-position');
    const chatMessages = document.getElementById('chat-messages');
    const chatText = document.getElementById('chat-text');
    const sendButton = document.getElementById('send-button');
    const viewControls = document.querySelectorAll('#view-controls button');
    
    // Movement control variables
    const movementControls = {
        forward: false,
        backward: false,
        left: false,
        right: false,
        up: false,
        down: false
    };
    
    // Socket.io connection
    const socket = io();
    
    // Event listeners
    startButton.addEventListener('click', startSimulation);
    loginButton.addEventListener('click', handleLogin);
    logoutButton.addEventListener('click', handleLogout);
    
    // Movement control listeners
    document.getElementById('move-forward').addEventListener('mousedown', () => movementControls.forward = true);
    document.getElementById('move-forward').addEventListener('mouseup', () => movementControls.forward = false);
    document.getElementById('move-backward').addEventListener('mousedown', () => movementControls.backward = true);
    document.getElementById('move-backward').addEventListener('mouseup', () => movementControls.backward = false);
    document.getElementById('move-left').addEventListener('mousedown', () => movementControls.left = true);
    document.getElementById('move-left').addEventListener('mouseup', () => movementControls.left = false);
    document.getElementById('move-right').addEventListener('mousedown', () => movementControls.right = true);
    document.getElementById('move-right').addEventListener('mouseup', () => movementControls.right = false);
    document.getElementById('move-up').addEventListener('mousedown', () => movementControls.up = true);
    document.getElementById('move-up').addEventListener('mouseup', () => movementControls.up = false);
    document.getElementById('move-down').addEventListener('mousedown', () => movementControls.down = true);
    document.getElementById('move-down').addEventListener('mouseup', () => movementControls.down = false);
    
    // Chat input listeners
    chatText.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
    
    sendButton.addEventListener('click', sendChatMessage);
    
    // Socket events
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    socket.on('chat_message', function(data) {
        addChatMessage(data.from, data.message);
    });
    
    socket.on('status_update', function(data) {
        updateStatus(data.status);
    });
    
    socket.on('teleport', function(data) {
        // Update region info in the UI
        updateRegionInfo(data.region, data.position);
        
        // Update marker on mini-map
        updateMiniMapMarker(data.position[0], data.position[1]);
        
        // If 3D avatar is available, update its position
        if (avatarManager) {
            avatarManager.setPosition(data.position[0], data.position[2], data.position[1]); // Note: Y and Z are swapped in Three.js
        }
        
        // Add log entry
        addLogEntry(`Teleported to ${data.region} at position ${data.position.join(', ')}`, 'info');
    });
    
    // Functions
    function startSimulation() {
        clearDisplay();
        
        // Disable start button during simulation
        startButton.disabled = true;
        startButton.textContent = 'Simulation Running...';
        
        // Update status
        updateStatus('starting');
        
        // Send start request to server
        fetch('/api/start', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log('Simulation started', data);
            
            // Start polling for events
            pollEvents();
            
            // Start movement loop if avatar exists
            if (avatarManager) {
                startMovementLoop();
            }
        })
        .catch(error => {
            console.error('Error starting simulation:', error);
            updateStatus('error');
            
            // Re-enable start button
            startButton.disabled = false;
            startButton.textContent = 'Start Simulation';
        });
    }
    
    function pollEvents() {
        // Poll every 500ms for new events
        const pollInterval = setInterval(function() {
            fetch('/api/state')
                .then(response => response.json())
                .then(data => {
                    // Check if simulation is completed
                    if (data.status === 'completed' || data.status === 'error') {
                        clearInterval(pollInterval);
                        
                        // Re-enable start button
                        startButton.disabled = false;
                        startButton.textContent = 'Restart Simulation';
                    }
                    
                    // Update user info if logged in
                    if (data.logged_in && data.user) {
                        loginStatus.textContent = 'Logged in';
                        userName.textContent = `Name: ${data.user.name}`;
                        userId.textContent = `ID: ${data.user.id}`;
                        updateLoginButtons(true);
                    } else {
                        loginStatus.textContent = data.status === 'completed' ? 'Logged out' : 'Not logged in';
                        userName.textContent = '';
                        userId.textContent = '';
                        updateLoginButtons(false);
                    }
                    
                    // Update region info if available
                    if (data.current_region) {
                        updateRegionInfo(data.current_region, data.position);
                        
                        // Update avatar position if we have one
                        if (data.position && avatarManager) {
                            avatarManager.setPosition(data.position[0], data.position[2], data.position[1]);
                        }
                    }
                })
                .catch(error => {
                    console.error('Error polling state:', error);
                });
                
            fetch('/api/events')
                .then(response => response.json())
                .then(events => {
                    // Process new events
                    events.forEach(event => {
                        processEvent(event);
                    });
                })
                .catch(error => {
                    console.error('Error polling events:', error);
                });
        }, 500);
    }
    
    function processEvent(event) {
        switch(event.type) {
            case 'log':
                addLogEntry(event.message, event.level.toLowerCase());
                break;
            case 'chat':
                // Chat messages are handled directly via socket.io
                break;
            case 'teleport':
                // Teleport events are handled directly via socket.io
                break;
            case 'login':
                loginStatus.textContent = 'Logged in';
                updateLoginButtons(true);
                addLogEntry('Login successful', 'info');
                break;
            case 'logout':
                loginStatus.textContent = 'Logged out';
                updateLoginButtons(false);
                addLogEntry('Logged out', 'info');
                break;
        }
    }
    
    function updateStatus(status) {
        // Remove all status classes
        statusIndicator.className = '';
        
        // Add new status class
        statusIndicator.classList.add(`status-${status}`);
        
        // Update text
        switch(status) {
            case 'idle':
                statusIndicator.textContent = 'Idle';
                break;
            case 'starting':
                statusIndicator.textContent = 'Starting...';
                break;
            case 'initializing':
                statusIndicator.textContent = 'Initializing...';
                break;
            case 'logging_in':
                statusIndicator.textContent = 'Logging in...';
                // Disable login button during login
                loginButton.disabled = true;
                break;
            case 'logged_in':
                statusIndicator.textContent = 'Logged in';
                // Update login buttons
                updateLoginButtons(true);
                break;
            case 'in_world':
                statusIndicator.textContent = 'In World';
                // Update login buttons
                updateLoginButtons(true);
                break;
            case 'logging_out':
                statusIndicator.textContent = 'Logging out...';
                // Disable logout button during logout
                logoutButton.disabled = true;
                break;
            case 'completed':
                statusIndicator.textContent = 'Completed';
                // Reset buttons
                loginButton.disabled = false;
                logoutButton.disabled = false;
                updateLoginButtons(false);
                break;
            case 'error':
                statusIndicator.textContent = 'Error';
                // Reset buttons
                loginButton.disabled = false;
                logoutButton.disabled = false;
                break;
            case 'running_simulation_1':
                statusIndicator.textContent = 'Running (1/3)';
                break;
            case 'running_simulation_2':
                statusIndicator.textContent = 'Running (2/3)';
                break;
            case 'running_simulation_3':
                statusIndicator.textContent = 'Running (3/3)';
                break;
            default:
                statusIndicator.textContent = status;
        }
    }
    
    function updateRegionInfo(region, position) {
        regionName.textContent = region || 'Not connected';
        if (position && position.length === 3) {
            regionPosition.textContent = `Position: ${position[0]}, ${position[1]}, ${position[2]}`;
        } else {
            regionPosition.textContent = 'Position: 0, 0, 0';
        }
    }
    
    function updateMiniMapMarker(x, y) {
        const mapMarker = document.getElementById('avatar-marker');
        if (!mapMarker) return;
        
        // Convert world coordinates to minimap percentages
        const mapX = (x / 256) * 100;
        const mapY = 100 - (y / 256) * 100; // Invert Y for screen coordinates
        
        // Update marker position
        mapMarker.style.left = `${mapX}%`;
        mapMarker.style.top = `${mapY}%`;
    }
    
    function addChatMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'chat-message';
        
        const senderElement = document.createElement('div');
        senderElement.className = 'chat-sender';
        senderElement.textContent = sender;
        
        const textElement = document.createElement('div');
        textElement.className = 'chat-text';
        textElement.textContent = message;
        
        messageElement.appendChild(senderElement);
        messageElement.appendChild(textElement);
        
        chatMessages.appendChild(messageElement);
        
        // Auto-scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function sendChatMessage() {
        const message = chatText.value.trim();
        if (message === '') return;
        
        // In demo mode, we simulate sending a chat message
        addChatMessage('You', message);
        addLogEntry(`Chat message sent: ${message}`, 'info');
        
        // Clear input field
        chatText.value = '';
    }
    
    function startMovementLoop() {
        let lastTime = 0;
        const moveSpeed = 5; // Units per second
        
        function moveAvatar(time) {
            // Calculate time delta
            const delta = (time - lastTime) / 1000; // Convert to seconds
            lastTime = time;
            
            // Only process movement if avatar and scene exist
            if (avatarManager && avatarManager.avatar && sceneManager) {
                // Get current position
                const position = avatarManager.avatar.position.clone();
                let moved = false;
                
                // Apply movement based on controls
                if (movementControls.forward) {
                    position.z -= moveSpeed * delta;
                    moved = true;
                }
                if (movementControls.backward) {
                    position.z += moveSpeed * delta;
                    moved = true;
                }
                if (movementControls.left) {
                    position.x -= moveSpeed * delta;
                    moved = true;
                }
                if (movementControls.right) {
                    position.x += moveSpeed * delta;
                    moved = true;
                }
                if (movementControls.up) {
                    position.y += moveSpeed * delta;
                    moved = true;
                }
                if (movementControls.down) {
                    position.y -= moveSpeed * delta;
                    moved = true;
                }
                
                // Update avatar position
                if (moved) {
                    avatarManager.setPosition(position.x, position.y, position.z);
                    
                    // Update mini-map marker (flipping z to y for 2D map)
                    updateMiniMapMarker(position.x, position.z);
                    
                    // Update position display
                    regionPosition.textContent = `Position: ${Math.round(position.x)}, ${Math.round(position.z)}, ${Math.round(position.y)}`;
                }
            }
            
            // Continue animation loop
            requestAnimationFrame(moveAvatar);
        }
        
        // Start animation loop
        requestAnimationFrame(moveAvatar);
    }
    
    function clearDisplay() {
        // Clear all dynamic content
        chatMessages.innerHTML = '';
        systemLog.innerHTML = '';
        loginStatus.textContent = 'Not logged in';
        userName.textContent = '';
        userId.textContent = '';
        regionName.textContent = 'Not connected';
        regionPosition.textContent = 'Position: 0, 0, 0';
        
        // Reset minimap marker
        updateMiniMapMarker(128, 128);
        
        // Reset 3D avatar position if available
        if (avatarManager) {
            avatarManager.setPosition(0, 0, 0);
        }
        
        // Reset login/logout buttons
        updateLoginButtons(false);
    }
    
    function handleLogin() {
        // Update status to logging in
        updateStatus('logging_in');
        addLogEntry('Logging in to Kitely...', 'info');
        
        // In the demo, we'll simulate a login request
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                first_name: 'Test',
                last_name: 'User',
                password: 'password123',
                grid: 'kitely'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update login status
                updateStatus('logged_in');
                loginStatus.textContent = 'Logged in';
                
                // Update user details
                if (data.user) {
                    userName.textContent = `Name: ${data.user.name}`;
                    userId.textContent = `ID: ${data.user.id}`;
                }
                
                // Update login/logout buttons
                updateLoginButtons(true);
                
                // Log success
                addLogEntry('Successfully logged in to Kitely', 'info');
            } else {
                // Show error message
                updateStatus('error');
                addLogEntry(`Login failed: ${data.message || 'Unknown error'}`, 'error');
                
                // Keep login button visible
                updateLoginButtons(false);
            }
        })
        .catch(error => {
            console.error('Error during login:', error);
            addLogEntry(`Login error: ${error.message}`, 'error');
            updateStatus('error');
            
            // Keep login button visible
            updateLoginButtons(false);
        });
    }
    
    function handleLogout() {
        // Update status to logging out
        updateStatus('logging_out');
        addLogEntry('Logging out from Kitely...', 'info');
        
        // In the demo, we'll simulate a logout request
        fetch('/api/logout', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update login status
                updateStatus('completed');
                loginStatus.textContent = 'Logged out';
                
                // Clear user details
                userName.textContent = '';
                userId.textContent = '';
                
                // Update login/logout buttons
                updateLoginButtons(false);
                
                // Log success
                addLogEntry('Successfully logged out from Kitely', 'info');
            } else {
                // Show error message
                updateStatus('error');
                addLogEntry(`Logout failed: ${data.message || 'Unknown error'}`, 'error');
            }
        })
        .catch(error => {
            console.error('Error during logout:', error);
            addLogEntry(`Logout error: ${error.message}`, 'error');
            updateStatus('error');
        });
    }
    
    function updateLoginButtons(isLoggedIn) {
        if (isLoggedIn) {
            // Show logout button, hide login button
            loginButton.style.display = 'none';
            logoutButton.style.display = 'block';
        } else {
            // Show login button, hide logout button
            loginButton.style.display = 'block';
            logoutButton.style.display = 'none';
        }
    }
    
    // Initialize with idle status
    updateStatus('idle');
    updateLoginButtons(false);
});
