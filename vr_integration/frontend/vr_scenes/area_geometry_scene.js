/**
 * Area and Geometry Scene
 * Interactive 3D shapes with draggable edges
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { BaseScene } from './base_scene.js';

export class AreaGeometryScene extends BaseScene {
    constructor(scene, config, mode) {
        super(scene, config, mode);
        this.shape = null;
        this.edgeHelpers = [];
        this.areaLabel = null;
        this.currentShape = 'kare'; // Default shape
    }

    init() {
        // Add lighting
        this.addLighting();

        // Add grid
        const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
        this.addObject(gridHelper);

        // Create initial shape (square)
        this.createShape('kare', 4);

        // Add UI controls based on mode
        if (this.mode === 'guided' || this.mode === 'full') {
            this.addShapeSelector();
        }
    }

    createShape(shapeType, size) {
        // Remove existing shape
        if (this.shape) {
            this.scene.remove(this.shape);
            this.edgeHelpers.forEach(helper => this.scene.remove(helper));
            this.edgeHelpers = [];
        }

        let geometry;
        const color = 0x667eea;

        switch (shapeType) {
            case 'kare':
                geometry = new THREE.BoxGeometry(size, 0.1, size);
                break;
            case 'dikdörtgen':
                geometry = new THREE.BoxGeometry(size * 1.5, 0.1, size);
                break;
            case 'üçgen':
                // Triangular prism
                const shape = new THREE.Shape();
                shape.moveTo(0, 0);
                shape.lineTo(size, 0);
                shape.lineTo(size / 2, size * 0.866);
                shape.lineTo(0, 0);
                geometry = new THREE.ExtrudeGeometry(shape, {
                    depth: 0.1,
                    bevelEnabled: false
                });
                geometry.rotateX(-Math.PI / 2);
                break;
            default:
                geometry = new THREE.BoxGeometry(size, 0.1, size);
        }

        const material = new THREE.MeshStandardMaterial({
            color: color,
            metalness: 0.3,
            roughness: 0.7
        });

        this.shape = new THREE.Mesh(geometry, material);
        this.shape.position.y = 0.05;
        this.shape.castShadow = true;
        this.shape.receiveShadow = true;
        this.addObject(this.shape);

        // Calculate and display area
        this.updateAreaLabel();

        // Add edge helpers if draggable
        if (this.config.draggable_edges) {
            this.addEdgeHelpers();
        }
    }

    addEdgeHelpers() {
        // Add visual helpers for edges (simplified - just corners)
        const box = new THREE.Box3().setFromObject(this.shape);
        const size = box.getSize(new THREE.Vector3());
        
        const helperGeometry = new THREE.SphereGeometry(0.2, 16, 16);
        const helperMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });

        // Add corner markers
        const corners = [
            new THREE.Vector3(-size.x/2, 0.2, -size.z/2),
            new THREE.Vector3(size.x/2, 0.2, -size.z/2),
            new THREE.Vector3(size.x/2, 0.2, size.z/2),
            new THREE.Vector3(-size.x/2, 0.2, size.z/2)
        ];

        corners.forEach(corner => {
            const helper = new THREE.Mesh(helperGeometry, helperMaterial);
            helper.position.copy(corner);
            this.addObject(helper);
            this.edgeHelpers.push(helper);
        });
    }

    updateAreaLabel() {
        if (!this.shape) return;

        const box = new THREE.Box3().setFromObject(this.shape);
        const size = box.getSize(new THREE.Vector3());
        const area = size.x * size.z;

        // Remove old label
        if (this.areaLabel) {
            this.scene.remove(this.areaLabel);
        }

        // Create text (simplified - using HTML overlay would be better)
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;
        context.fillStyle = 'white';
        context.font = '24px Arial';
        context.fillText(`Alan: ${area.toFixed(2)} cm²`, 10, 40);

        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        this.areaLabel = new THREE.Sprite(spriteMaterial);
        this.areaLabel.position.set(0, 3, 0);
        this.areaLabel.scale.set(2, 0.5, 1);
        this.addObject(this.areaLabel);
    }

    addShapeSelector() {
        // Add shape selector buttons (simplified - would be better as HTML UI)
        console.log('Shape selector available. Use createShape(type) to change shapes.');
    }

    update() {
        // Animate if needed
        if (this.shape && this.mode === 'full') {
            this.shape.rotation.y += 0.005;
        }
    }
}

