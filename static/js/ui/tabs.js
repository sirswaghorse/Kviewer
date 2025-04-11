/**
 * KitelyView - UI Manager
 * Handles tab switching and panel toggles for slide-out panels
 */

class UIManager {
    constructor() {
        // Tab elements
        this.tabs = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
        
        // Panel elements
        this.leftPanel = document.getElementById('left-panel');
        this.rightPanel = document.getElementById('right-panel');
        this.chatArea = document.getElementById('chat-area');
        
        // Button elements - toolbar
        this.toggleLeftBtn = document.getElementById('toggle-left-button');
        this.toggleRightBtn = document.getElementById('toggle-right-button');
        this.toggleChatBtn = document.getElementById('toggle-chat-button');
        
        // Button elements - HUD
        this.leftPanelBtn = document.getElementById('left-panel-button');
        this.rightPanelBtn = document.getElementById('right-panel-button');
        this.chatPanelBtn = document.getElementById('chat-panel-button');
        
        // Initialize panel states
        this.leftPanelVisible = false;
        this.rightPanelVisible = false;
        this.chatAreaVisible = false;
        
        this.initTabEvents();
        this.initPanelToggleEvents();
        this.initCloseEvents();
    }
    
    initTabEvents() {
        // Add click event to each tab button
        this.tabs.forEach(tab => {
            tab.addEventListener('click', (event) => {
                const tabName = event.currentTarget.getAttribute('data-tab');
                if (tabName) {
                    this.switchTab(tabName);
                }
            });
        });
    }
    
    initPanelToggleEvents() {
        // Toolbar buttons
        if (this.toggleLeftBtn) {
            this.toggleLeftBtn.addEventListener('click', () => this.toggleLeftPanel());
        }
        
        if (this.toggleRightBtn) {
            this.toggleRightBtn.addEventListener('click', () => this.toggleRightPanel());
        }
        
        if (this.toggleChatBtn) {
            this.toggleChatBtn.addEventListener('click', () => this.toggleChatArea());
        }
        
        // HUD buttons
        if (this.leftPanelBtn) {
            this.leftPanelBtn.addEventListener('click', () => this.toggleLeftPanel());
        }
        
        if (this.rightPanelBtn) {
            this.rightPanelBtn.addEventListener('click', () => this.toggleRightPanel());
        }
        
        if (this.chatPanelBtn) {
            this.chatPanelBtn.addEventListener('click', () => this.toggleChatArea());
        }
        
        // Add keyboard shortcuts
        document.addEventListener('keydown', (event) => {
            // Alt+1 for left panel
            if (event.altKey && event.key === '1') {
                this.toggleLeftPanel();
            }
            
            // Alt+2 for right panel
            if (event.altKey && event.key === '2') {
                this.toggleRightPanel();
            }
            
            // Alt+3 for chat panel
            if (event.altKey && event.key === '3') {
                this.toggleChatArea();
            }
            
            // Escape to close all panels
            if (event.key === 'Escape') {
                this.closeAllPanels();
            }
        });
    }
    
    initCloseEvents() {
        // Close panels when clicking on the main view (if not clicking on a control)
        const mainView = document.getElementById('main-view');
        if (mainView) {
            mainView.addEventListener('click', (event) => {
                // Don't close if clicking on a control or if the click originated from a panel
                if (!event.target.closest('#controls-overlay') && 
                    !event.target.closest('.hud-button')) {
                    this.closeAllPanels();
                }
            });
        }
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
        const selectedTab = document.querySelector(`.tab-button[data-tab="${tabName}"]`);
        const selectedContent = document.getElementById(`${tabName}-tab`);
        
        if (selectedTab) {
            selectedTab.classList.add('active');
        }
        
        if (selectedContent) {
            selectedContent.classList.add('active');
        }
    }
    
    toggleLeftPanel() {
        this.leftPanelVisible = !this.leftPanelVisible;
        
        if (this.leftPanelVisible) {
            this.leftPanel.classList.add('visible');
            // Close other panels to prevent overlap
            this.rightPanel.classList.remove('visible');
            this.chatArea.classList.remove('visible');
            this.rightPanelVisible = false;
            this.chatAreaVisible = false;
        } else {
            this.leftPanel.classList.remove('visible');
        }
    }
    
    toggleRightPanel() {
        this.rightPanelVisible = !this.rightPanelVisible;
        
        if (this.rightPanelVisible) {
            this.rightPanel.classList.add('visible');
            // Close other panels to prevent overlap
            this.leftPanel.classList.remove('visible');
            this.chatArea.classList.remove('visible');
            this.leftPanelVisible = false;
            this.chatAreaVisible = false;
        } else {
            this.rightPanel.classList.remove('visible');
        }
    }
    
    toggleChatArea() {
        this.chatAreaVisible = !this.chatAreaVisible;
        
        if (this.chatAreaVisible) {
            this.chatArea.classList.add('visible');
            // Close other panels to prevent overlap
            this.leftPanel.classList.remove('visible');
            this.rightPanel.classList.remove('visible');
            this.leftPanelVisible = false;
            this.rightPanelVisible = false;
        } else {
            this.chatArea.classList.remove('visible');
        }
    }
    
    closeAllPanels() {
        this.leftPanel.classList.remove('visible');
        this.rightPanel.classList.remove('visible');
        this.chatArea.classList.remove('visible');
        this.leftPanelVisible = false;
        this.rightPanelVisible = false;
        this.chatAreaVisible = false;
    }
}

// Initialize UI manager when DOM is loaded
let uiManager;
document.addEventListener('DOMContentLoaded', () => {
    uiManager = new UIManager();
});