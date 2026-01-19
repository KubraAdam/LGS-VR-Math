/**
 * Number Line Scene
 * 3D number line with square root point visualization
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { BaseScene } from './base_scene.js';

export class NumberLineScene extends BaseScene {
    constructor(scene, config, mode) {
        super(scene, config, mode);
        this.numberLine = null;
        this.sqrtPoint = null;
        this.sqrtValue = 17; // Default: √17
        this.nearestIntegers = [];
    }

    init() {
        // Add lighting
        this.addLighting();

        // Create number line
        this.createNumberLine();

        // Add square root point
        this.updateSqrtPoint(this.sqrtValue);
    }

    createNumberLine() {
        const range = this.config.number_range || [-10, 10];
        const length = range[1] - range[0];

        // Main line
        const lineGeometry = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(range[0], 0, 0),
            new THREE.Vector3(range[1], 0, 0)
        ]);
        const lineMaterial = new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 3 });
        this.numberLine = new THREE.Line(lineGeometry, lineMaterial);
        this.addObject(this.numberLine);

        // Tick marks and labels
        for (let i = range[0]; i <= range[1]; i++) {
            // Tick mark
            const tickGeometry = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(i, -0.2, 0),
                new THREE.Vector3(i, 0.2, 0)
            ]);
            const tick = new THREE.Line(tickGeometry, lineMaterial);
            this.addObject(tick);

            // Label (simplified - using sprites)
            if (i % 5 === 0 || Math.abs(i) <= 3) {
                this.addNumberLabel(i);
            }
        }
    }

    addNumberLabel(value) {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 64;
        canvas.height = 64;
        context.fillStyle = 'white';
        context.font = '20px Arial';
        context.textAlign = 'center';
        context.fillText(value.toString(), 32, 40);

        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.position.set(value, 0.5, 0);
        sprite.scale.set(0.5, 0.5, 1);
        this.addObject(sprite);
    }

    updateSqrtPoint(value) {
        this.sqrtValue = value;
        const sqrtResult = Math.sqrt(value);
        const floor = Math.floor(sqrtResult);
        const ceil = Math.ceil(sqrtResult);

        // Remove old point
        if (this.sqrtPoint) {
            this.scene.remove(this.sqrtPoint);
        }
        this.nearestIntegers.forEach(obj => this.scene.remove(obj));
        this.nearestIntegers = [];

        // Create glowing point for √n
        const pointGeometry = new THREE.SphereGeometry(0.3, 16, 16);
        const pointMaterial = new THREE.MeshStandardMaterial({
            color: 0x00ff00,
            emissive: 0x00ff00,
            emissiveIntensity: 0.8
        });
        this.sqrtPoint = new THREE.Mesh(pointGeometry, pointMaterial);
        this.sqrtPoint.position.set(sqrtResult, 0.3, 0);
        this.addObject(this.sqrtPoint);

        // Highlight nearest integers
        if (this.config.highlight_nearest_integers) {
            [floor, ceil].forEach(int => {
                const highlightGeometry = new THREE.BoxGeometry(0.4, 0.1, 0.4);
                const highlightMaterial = new THREE.MeshBasicMaterial({
                    color: 0xffff00,
                    transparent: true,
                    opacity: 0.5
                });
                const highlight = new THREE.Mesh(highlightGeometry, highlightMaterial);
                highlight.position.set(int, 0.05, 0);
                this.addObject(highlight);
                this.nearestIntegers.push(highlight);
            });
        }

        // Add label
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 128;
        canvas.height = 64;
        context.fillStyle = '#00ff00';
        context.font = 'bold 20px Arial';
        context.textAlign = 'center';
        context.fillText(`√${value} ≈ ${sqrtResult.toFixed(2)}`, 64, 40);

        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
        const label = new THREE.Sprite(spriteMaterial);
        label.position.set(sqrtResult, 1, 0);
        label.scale.set(1, 0.5, 1);
        this.addObject(label);
    }

    update() {
        // Animate point if in full mode
        if (this.sqrtPoint && this.mode === 'full') {
            this.sqrtPoint.rotation.y += 0.02;
        }
    }
}

