/**
 * KitelyView - Tab Manager
 * Handles tab switching for the sidebar panels
 */

class TabManager {
    constructor() {
        this.tabs = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
        
        this.initTabEvents();
    }
    
    initTabEvents() {
        // Add click event to each tab button
        this.tabs.forEach(tab => {
            tab.addEventListener('click', (event) => {
                this.switchTab(event.target.getAttribute('data-tab'));
            });
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
}

// Initialize tab manager when DOM is loaded
let tabManager;
document.addEventListener('DOMContentLoaded', () => {
    tabManager = new TabManager();
});