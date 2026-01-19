/**
 * Base Scene Class
 * Base class for all VR scenes
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

export class BaseScene {
    constructor(scene, config, mode) {
        this.scene = scene;
        this.config = config;
        this.mode = mode;
        this.objects = [];
    }

    /**
     * Initialize scene - to be implemented by subclasses
     */
    init() {
        throw new Error('init() must be implemented by subclass');
    }

    /**
     * Update scene - to be implemented by subclasses
     */
    update() {
        // Default: no update needed
    }

    /**
     * Cleanup scene
     */
    cleanup() {
        this.objects.forEach(obj => {
            if (obj.geometry) obj.geometry.dispose();
            if (obj.material) {
                if (Array.isArray(obj.material)) {
                    obj.material.forEach(m => m.dispose());
                } else {
                    obj.material.dispose();
                }
            }
            this.scene.remove(obj);
        });
        this.objects = [];
    }

    /**
     * Add object to scene and track it
     */
    addObject(object) {
        this.scene.add(object);
        this.objects.push(object);
        return object;
    }

    /**
     * Add lighting
     */
    addLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.addObject(ambientLight);

        // Directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(5, 10, 5);
        directionalLight.castShadow = true;
        this.addObject(directionalLight);

        // Point light
        const pointLight = new THREE.PointLight(0xffffff, 0.5);
        pointLight.position.set(-5, 5, -5);
        this.addObject(pointLight);
    }
}

