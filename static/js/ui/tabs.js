/**
 * KitelyView - UI Manager
 * Handles tab switching and panel toggles for Firestorm-like layout
 */

class UIManager {
    constructor() {
        this.tabs = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
        this.leftPanel = document.getElementById('left-panel');
        this.rightPanel = document.getElementById('right-panel');
        this.leftPanelToggle = document.getElementById('left-panel-toggle');
        this.rightPanelToggle = document.getElementById('right-panel-toggle');
        
        this.initTabEvents();
        this.initPanelToggleEvents();
        
        // Store panel states
        this.leftPanelCollapsed = false;
        this.rightPanelCollapsed = false;
    }
    
    initTabEvents() {
        // Add click event to each tab button
        this.tabs.forEach(tab => {
            tab.addEventListener('click', (event) => {
                this.switchTab(event.target.getAttribute('data-tab'));
            });
        });
    }
    
    initPanelToggleEvents() {
        // Left panel toggle
        this.leftPanelToggle.addEventListener('click', () => {
            this.toggleLeftPanel();
        });
        
        // Right panel toggle
        this.rightPanelToggle.addEventListener('click', () => {
            this.toggleRightPanel();
        });
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            // Ctrl+Alt+[ to toggle left panel
            if (event.ctrlKey && event.altKey && event.key === '[') {
                this.toggleLeftPanel();
            }
            
            // Ctrl+Alt+] to toggle right panel
            if (event.ctrlKey && event.altKey && event.key === ']') {
                this.toggleRightPanel();
            }
        });
    }
    
    switchTab(tabName) {
        // Remove active class from all tabs and contents
        this.tabs.forEach(tab => {
            tab.classList.remove('active');
        });
        
        this.tabContents.forEach(content => {
            content.classList.remove('active');
        });
        
        // Add active class to selected tab and content
        document.querySelector(`.tab-button[data-tab="${tabName}"]`).classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
    }
    
    toggleLeftPanel() {
        this.leftPanelCollapsed = !this.leftPanelCollapsed;
        
        if (this.leftPanelCollapsed) {
            this.leftPanel.classList.add('collapsed');
            this.leftPanelToggle.textContent = '►';
            this.leftPanelToggle.title = 'Show Left Panel';
        } else {
            this.leftPanel.classList.remove('collapsed');
            this.leftPanelToggle.textContent = '◄';
            this.leftPanelToggle.title = 'Hide Left Panel';
        }
    }
    
    toggleRightPanel() {
        this.rightPanelCollapsed = !this.rightPanelCollapsed;
        
        if (this.rightPanelCollapsed) {
            this.rightPanel.classList.add('collapsed');
            this.rightPanelToggle.textContent = '◄';
            this.rightPanelToggle.title = 'Show Right Panel';
        } else {
            this.rightPanel.classList.remove('collapsed');
            this.rightPanelToggle.textContent = '►';
            this.rightPanelToggle.title = 'Hide Right Panel';
        }
    }
}

// Initialize UI manager when DOM is loaded
let uiManager;
document.addEventListener('DOMContentLoaded', () => {
    uiManager = new UIManager();
});