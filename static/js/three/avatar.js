/**
 * KitelyView - Avatar Model Manager
 * Handles the 3D avatar creation and customization
 */

class AvatarManager {
    constructor(sceneManager) {
        this.sceneManager = sceneManager;
        this.avatar = null;
        this.avatarHeight = 1.0;
        this.bodyShape = 'athletic';
        this.skinColor = '#f2d2bd';
        this.hairStyle = 'short';
        this.hairColor = '#523b22';
        this.outfitStyle = 'casual';
        this.outfitPrimaryColor = '#3f51b5';
        this.outfitSecondaryColor = '#f44336';
        
        this.init();
    }
    
    init() {
        // Create initial avatar
        this.createAvatar();
    }
    
    createAvatar() {
        // Remove existing avatar if any
        if (this.avatar) {
            this.sceneManager.scene.remove(this.avatar);
        }
        
        // Create avatar group
        this.avatar = new THREE.Group();
        
        // Create body parts based on current settings
        this.createHead();
        this.createTorso();
        this.createArms();
        this.createLegs();
        
        // Position avatar
        this.avatar.position.y = 0;
        
        // Add to scene
        this.sceneManager.scene.add(this.avatar);
    }
    
    createHead() {
        // Create head geometry
        const headGeometry = new THREE.SphereGeometry(0.25, 32, 32);
        const headMaterial = new THREE.MeshStandardMaterial({ color: new THREE.Color(this.skinColor) });
        const head = new THREE.Mesh(headGeometry, headMaterial);
        head.position.y = 1.6 * this.avatarHeight;
        head.castShadow = true;
        
        // Create hair based on hair style
        let hairGeometry;
        switch (this.hairStyle) {
            case 'short':
                hairGeometry = new THREE.SphereGeometry(0.27, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2);
                break;
            case 'ponytail':
                hairGeometry = new THREE.CylinderGeometry(0.05, 0.1, 0.4, 16);
                break;
            case 'long':
                hairGeometry = new THREE.CylinderGeometry(0.25, 0.15, 0.6, 16);
                break;
            default:
                hairGeometry = new THREE.SphereGeometry(0.27, 32, 32, 0, Math.PI * 2, 0, Math.PI / 2);
        }
        
        const hairMaterial = new THREE.MeshStandardMaterial({ color: new THREE.Color(this.hairColor) });
        const hair = new THREE.Mesh(hairGeometry, hairMaterial);
        
        // Position hair based on style
        if (this.hairStyle === 'short') {
            hair.position.y = 1.6 * this.avatarHeight + 0.03;
            hair.rotation.x = Math.PI;
        } else if (this.hairStyle === 'ponytail') {
            hair.position.y = 1.6 * this.avatarHeight + 0.05;
            hair.position.z = -0.2;
        } else if (this.hairStyle === 'long') {
            hair.position.y = 1.45 * this.avatarHeight;
        }
        
        hair.castShadow = true;
        
        // Create face features
        const eyeGeometry = new THREE.SphereGeometry(0.05, 16, 16);
        const eyeMaterial = new THREE.MeshBasicMaterial({ color: 0x444444 });
        
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        leftEye.position.set(-0.1, 1.63 * this.avatarHeight, 0.2);
        
        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        rightEye.position.set(0.1, 1.63 * this.avatarHeight, 0.2);
        
        const mouthGeometry = new THREE.BoxGeometry(0.1, 0.03, 0.03);
        const mouthMaterial = new THREE.MeshBasicMaterial({ color: 0xcc6666 });
        const mouth = new THREE.Mesh(mouthGeometry, mouthMaterial);
        mouth.position.set(0, 1.53 * this.avatarHeight, 0.22);
        
        // Add all head parts to the avatar
        this.avatar.add(head);
        this.avatar.add(hair);
        this.avatar.add(leftEye);
        this.avatar.add(rightEye);
        this.avatar.add(mouth);
    }
    
    createTorso() {
        // Adjust torso shape based on body shape
        let width, depth;
        switch (this.bodyShape) {
            case 'athletic':
                width = 0.5;
                depth = 0.25;
                break;
            case 'slim':
                width = 0.4;
                depth = 0.2;
                break;
            case 'heavy':
                width = 0.6;
                depth = 0.35;
                break;
            default:
                width = 0.5;
                depth = 0.25;
        }
        
        // Create torso
        const torsoGeometry = new THREE.BoxGeometry(width, 0.6 * this.avatarHeight, depth);
        
        // Create material based on outfit style
        let torsoMaterial;
        switch (this.outfitStyle) {
            case 'casual':
                torsoMaterial = new THREE.MeshStandardMaterial({ color: new THREE.Color(this.outfitPrimaryColor) });
                break;
            case 'formal':
                torsoMaterial = new THREE.MeshStandardMaterial({ 
                    color: new THREE.Color(this.outfitPrimaryColor),
                    metalness: 0.3,
                    roughness: 0.7
                });
                break;
            case 'fantasy':
                torsoMaterial = new THREE.MeshStandardMaterial({ 
                    color: new THREE.Color(this.outfitPrimaryColor),
                    metalness: 0.5,
                    roughness: 0.5
                });
                break;
            default:
                torsoMaterial = new THREE.MeshStandardMaterial({ color: new THREE.Color(this.outfitPrimaryColor) });
        }
        
        const torso = new THREE.Mesh(torsoGeometry, torsoMaterial);
        torso.position.y = 1.2 * this.avatarHeight;
        torso.castShadow = true;
        
        this.avatar.add(torso);
    }
    
    createArms() {
        // Adjust arm dimensions based on body shape
        let thickness;
        switch (this.bodyShape) {
            case 'athletic':
                thickness = 0.12;
                break;
            case 'slim':
                thickness = 0.1;
                break;
            case 'heavy':
                thickness = 0.15;
                break;
            default:
                thickness = 0.12;
        }
        
        // Create arm material based on outfit
        const armMaterial = new THREE.MeshStandardMaterial({ color: new THREE.Color(this.outfitSecondaryColor) });
        
        // Left arm
        const leftArmGeometry = new THREE.BoxGeometry(thickness, 0.6 * this.avatarHeight, thickness);
        const leftArm = new THREE.Mesh(leftArmGeometry, armMaterial);
        leftArm.position.set(-0.3 - thickness/2, 1.2 * this.avatarHeight, 0);
        leftArm.castShadow = true;
        
        // Right arm
        const rightArmGeometry = new THREE.BoxGeometry(thickness, 0.6 * this.avatarHeight, thickness);
        const rightArm = new THREE.Mesh(rightArmGeometry, armMaterial);
        rightArm.position.set(0.3 + thickness/2, 1.2 * this.avatarHeight, 0);
        rightArm.castShadow = true;
        
        // Add hands
        const handGeometry = new THREE.SphereGeometry(thickness * 0.8, 16, 16);
        const handMaterial = new THREE.MeshStandardMaterial({ color: new THREE.Color(this.skinColor) });
        
        const leftHand = new THREE.Mesh(handGeometry, handMaterial);
        leftHand.position.set(-0.3 - thickness/2, 0.9 * this.avatarHeight, 0);
        leftHand.castShadow = true;
        
        const rightHand = new THREE.Mesh(handGeometry, handMaterial);
        rightHand.position.set(0.3 + thickness/2, 0.9 * this.avatarHeight, 0);
        rightHand.castShadow = true;
        
        this.avatar.add(leftArm);
        this.avatar.add(rightArm);
        this.avatar.add(leftHand);
        this.avatar.add(rightHand);
    }
    
    createLegs() {
        // Adjust leg dimensions based on body shape
        let thickness;
        switch (this.bodyShape) {
            case 'athletic':
                thickness = 0.15;
                break;
            case 'slim':
                thickness = 0.12;
                break;
            case 'heavy':
                thickness = 0.18;
                break;
            default:
                thickness = 0.15;
        }
        
        // Create leg material based on outfit
        const legMaterial = new THREE.MeshStandardMaterial({ color: new THREE.Color(this.outfitSecondaryColor) });
        
        // Left leg
        const leftLegGeometry = new THREE.BoxGeometry(thickness, 0.9 * this.avatarHeight, thickness);
        const leftLeg = new THREE.Mesh(leftLegGeometry, legMaterial);
        leftLeg.position.set(-0.15, 0.45 * this.avatarHeight, 0);
        leftLeg.castShadow = true;
        
        // Right leg
        const rightLegGeometry = new THREE.BoxGeometry(thickness, 0.9 * this.avatarHeight, thickness);
        const rightLeg = new THREE.Mesh(rightLegGeometry, legMaterial);
        rightLeg.position.set(0.15, 0.45 * this.avatarHeight, 0);
        rightLeg.castShadow = true;
        
        // Create shoes
        const shoeGeometry = new THREE.BoxGeometry(thickness * 1.2, thickness * 0.5, thickness * 1.5);
        const shoeMaterial = new THREE.MeshStandardMaterial({ color: 0x222222 });
        
        const leftShoe = new THREE.Mesh(shoeGeometry, shoeMaterial);
        leftShoe.position.set(-0.15, thickness * 0.25, thickness * 0.25);
        leftShoe.castShadow = true;
        
        const rightShoe = new THREE.Mesh(shoeGeometry, shoeMaterial);
        rightShoe.position.set(0.15, thickness * 0.25, thickness * 0.25);
        rightShoe.castShadow = true;
        
        this.avatar.add(leftLeg);
        this.avatar.add(rightLeg);
        this.avatar.add(leftShoe);
        this.avatar.add(rightShoe);
    }
    
    updateAppearance(appearance) {
        // Update appearance settings
        if (appearance.height !== undefined) this.avatarHeight = appearance.height;
        if (appearance.bodyShape !== undefined) this.bodyShape = appearance.bodyShape;
        if (appearance.skinColor !== undefined) this.skinColor = appearance.skinColor;
        if (appearance.hairStyle !== undefined) this.hairStyle = appearance.hairStyle;
        if (appearance.hairColor !== undefined) this.hairColor = appearance.hairColor;
        if (appearance.outfitStyle !== undefined) this.outfitStyle = appearance.outfitStyle;
        if (appearance.outfitPrimaryColor !== undefined) this.outfitPrimaryColor = appearance.outfitPrimaryColor;
        if (appearance.outfitSecondaryColor !== undefined) this.outfitSecondaryColor = appearance.outfitSecondaryColor;
        
        // Recreate avatar with new settings
        this.createAvatar();
    }
    
    setPosition(x, y, z) {
        if (this.avatar) {
            this.avatar.position.set(x, y, z);
        }
    }
}

// Initialize avatar manager after scene is created
let avatarManager;
document.addEventListener('DOMContentLoaded', () => {
    // Wait for scene manager to be initialized
    setTimeout(() => {
        if (sceneManager) {
            avatarManager = new AvatarManager(sceneManager);
        }
    }, 100);
});