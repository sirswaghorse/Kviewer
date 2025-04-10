/**
 * KitelyView - Appearance Manager
 * Handles avatar appearance customization
 */

class AppearanceManager {
    constructor() {
        this.heightSlider = document.getElementById('avatar-height');
        this.bodyShapeSelect = document.getElementById('body-shape');
        this.skinColorPicker = document.getElementById('skin-color');
        this.hairStyleSelect = document.getElementById('hair-style');
        this.hairColorPicker = document.getElementById('hair-color');
        this.outfitStyleSelect = document.getElementById('outfit-style');
        this.outfitPrimaryColorPicker = document.getElementById('outfit-primary-color');
        this.outfitSecondaryColorPicker = document.getElementById('outfit-secondary-color');
        this.applyButton = document.getElementById('apply-appearance');
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Apply button click event
        this.applyButton.addEventListener('click', () => {
            this.applyAppearanceChanges();
        });
    }
    
    applyAppearanceChanges() {
        // Only proceed if avatarManager is initialized
        if (!avatarManager) {
            addLogEntry('Avatar manager not initialized', 'error');
            return;
        }
        
        // Get current values from UI controls
        const appearance = {
            height: parseFloat(this.heightSlider.value),
            bodyShape: this.bodyShapeSelect.value,
            skinColor: this.skinColorPicker.value,
            hairStyle: this.hairStyleSelect.value,
            hairColor: this.hairColorPicker.value,
            outfitStyle: this.outfitStyleSelect.value,
            outfitPrimaryColor: this.outfitPrimaryColorPicker.value,
            outfitSecondaryColor: this.outfitSecondaryColorPicker.value
        };
        
        // Update avatar appearance
        avatarManager.updateAppearance(appearance);
        
        // Add log entry
        addLogEntry('Avatar appearance updated', 'info');
    }
    
    // Load appearance values into UI controls
    loadAppearanceValues(appearance) {
        if (!appearance) return;
        
        if (appearance.height !== undefined) this.heightSlider.value = appearance.height;
        if (appearance.bodyShape !== undefined) this.bodyShapeSelect.value = appearance.bodyShape;
        if (appearance.skinColor !== undefined) this.skinColorPicker.value = appearance.skinColor;
        if (appearance.hairStyle !== undefined) this.hairStyleSelect.value = appearance.hairStyle;
        if (appearance.hairColor !== undefined) this.hairColorPicker.value = appearance.hairColor;
        if (appearance.outfitStyle !== undefined) this.outfitStyleSelect.value = appearance.outfitStyle;
        if (appearance.outfitPrimaryColor !== undefined) this.outfitPrimaryColorPicker.value = appearance.outfitPrimaryColor;
        if (appearance.outfitSecondaryColor !== undefined) this.outfitSecondaryColorPicker.value = appearance.outfitSecondaryColor;
    }
}

// Initialize appearance manager when DOM is loaded
let appearanceManager;
document.addEventListener('DOMContentLoaded', () => {
    appearanceManager = new AppearanceManager();
});