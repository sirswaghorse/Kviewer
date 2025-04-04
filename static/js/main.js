document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const startButton = document.getElementById('start-button');
    const statusIndicator = document.getElementById('status-indicator');
    const loginStatus = document.getElementById('login-status');
    const userName = document.getElementById('user-name');
    const userId = document.getElementById('user-id');
    const regionName = document.getElementById('region-name');
    const regionPosition = document.getElementById('region-position');
    const chatMessages = document.getElementById('chat-messages');
    const systemLog = document.getElementById('system-log');
    const chatText = document.getElementById('chat-text');
    const sendButton = document.getElementById('send-button');
    const avatar = document.getElementById('avatar');
    const avatarMarker = document.getElementById('avatar-marker');
    
    // Socket.io connection
    const socket = io();
    
    // Event listeners
    startButton.addEventListener('click', startSimulation);
    
    // Connect to server
    socket.on('connect', function() {
        console.log('Connected to server');
    });
    
    // Handle chat messages
    socket.on('chat_message', function(data) {
        addChatMessage(data.from, data.message);
        
        // Auto-scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    });
    
    // Handle status updates
    socket.on('status_update', function(data) {
        updateStatus(data.status);
    });
    
    // Handle teleport events
    socket.on('teleport', function(data) {
        updateRegionInfo(data.region, data.position);
        
        // Move avatar on the screen
        const x = (data.position[0] / 256) * 100; // Scale to percentage
        const y = 100 - (data.position[1] / 256) * 100; // Invert Y axis and scale
        
        // Update avatar position with animation
        avatar.style.left = `${x}%`;
        avatar.style.bottom = `${40 + (data.position[2] / 100) * 10}%`; // Height based on Z
        
        // Update mini-map marker
        avatarMarker.style.left = `${x}%`;
        avatarMarker.style.top = `${y}%`;
        
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
                    } else {
                        loginStatus.textContent = data.status === 'completed' ? 'Logged out' : 'Not logged in';
                        userName.textContent = '';
                        userId.textContent = '';
                    }
                    
                    // Update region info if available
                    if (data.current_region) {
                        updateRegionInfo(data.current_region, data.position);
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
                addLogEntry('Login successful', 'info');
                break;
            case 'logout':
                loginStatus.textContent = 'Logged out';
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
                break;
            case 'logged_in':
                statusIndicator.textContent = 'Logged in';
                break;
            case 'in_world':
                statusIndicator.textContent = 'In World';
                break;
            case 'logging_out':
                statusIndicator.textContent = 'Logging out...';
                break;
            case 'completed':
                statusIndicator.textContent = 'Completed';
                break;
            case 'error':
                statusIndicator.textContent = 'Error';
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
    }
    
    function addLogEntry(message, level) {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry log-${level}`;
        logEntry.textContent = message;
        
        systemLog.appendChild(logEntry);
        
        // Auto-scroll to bottom
        systemLog.scrollTop = systemLog.scrollHeight;
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
        
        // Reset avatar position
        avatar.style.left = '50%';
        avatar.style.bottom = '40%';
        
        // Reset minimap marker
        avatarMarker.style.left = '50%';
        avatarMarker.style.top = '50%';
    }
    
    // Initialize with idle status
    updateStatus('idle');
});
