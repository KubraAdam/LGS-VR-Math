/**
 * VR Scene Manager
 * Manages loading and rendering of different VR scenes
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

// Scene instances
import { AreaGeometryScene } from './area_geometry_scene.js';
import { NumberLineScene } from './number_line_scene.js';
import { ComparisonScene } from './comparison_scene.js';
import { AreaPerimeterScene } from './area_perimeter_scene.js';

class SceneManager {
    constructor() {
        this.canvas = document.getElementById('vr-canvas');
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.currentScene = null;
        this.animationId = null;
    }

    /**
     * Initialize Three.js renderer
     */
    initRenderer() {
        if (this.renderer) {
            return; // Already initialized
        }

        if (!this.canvas) {
            console.error('Canvas element not found!');
            throw new Error('Canvas element not found');
        }

        console.log('Initializing Three.js renderer...');
        console.log('Canvas size:', this.canvas.clientWidth, 'x', this.canvas.clientHeight);

        // Scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);

        // Camera
        const aspect = this.canvas.clientWidth / this.canvas.clientHeight || 1;
        this.camera = new THREE.PerspectiveCamera(
            75,
            aspect,
            0.1,
            1000
        );
        this.camera.position.set(0, 5, 10);
        this.camera.lookAt(0, 0, 0);

        // Renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true
        });
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
        this.renderer.shadowMap.enabled = true;

        // Controls
        this.controls = new OrbitControls(this.camera, this.canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());

        console.log('Renderer initialized successfully');
    }

    /**
     * Load a VR scene
     */
    loadScene(sceneType, config, mode) {
        try {
            console.log('Loading VR scene:', sceneType, 'with mode:', mode);
            
            // Clean up previous scene
            this.cleanup();

            // Initialize renderer if needed
            this.initRenderer();

            // Create scene based on type
            switch (sceneType) {
                case 'area_geometry':
                    this.currentScene = new AreaGeometryScene(this.scene, config, mode);
                    break;
                case 'area_perimeter':
                    this.currentScene = new AreaPerimeterScene(this.scene, config, mode);
                    break;
                case 'number_line':
                    this.currentScene = new NumberLineScene(this.scene, config, mode);
                    break;
                case 'comparison':
                    this.currentScene = new ComparisonScene(this.scene, config, mode);
                    break;
                default:
                    console.error('Unknown scene type:', sceneType);
                    throw new Error(`Unknown scene type: ${sceneType}`);
            }

            // Initialize scene
            console.log('Initializing scene...');
            this.currentScene.init();
            console.log('Scene initialized successfully');

            // Start animation loop
            this.animate();
            console.log('Animation loop started');
        } catch (error) {
            console.error('Error loading VR scene:', error);
            throw error;
        }
    }

    /**
     * Animation loop
     */
    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());

        if (this.controls) {
            this.controls.update();
        }

        if (this.currentScene && this.currentScene.update) {
            this.currentScene.update();
        }

        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    /**
     * Handle window resize
     */
    onWindowResize() {
        if (!this.camera || !this.renderer || !this.canvas) return;

        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        
        this.camera.aspect = width / height || 1;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }

    /**
     * Cleanup current scene
     */
    cleanup() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }

        if (this.currentScene && this.currentScene.cleanup) {
            this.currentScene.cleanup();
        }

        if (this.scene) {
            // Remove all objects
            while (this.scene.children.length > 0) {
                this.scene.remove(this.scene.children[0]);
            }
        }

        this.currentScene = null;
    }
}

// Singleton instance
let sceneManager = null;

export function getSceneManager() {
    if (!sceneManager) {
        sceneManager = new SceneManager();
    }
    return sceneManager;
}

