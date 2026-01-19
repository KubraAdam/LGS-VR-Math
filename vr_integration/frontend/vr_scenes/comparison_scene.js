/**
 * Comparison and Sorting Scene
 * 3D bar chart for comparing square root values
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { BaseScene } from './base_scene.js';

export class ComparisonScene extends BaseScene {
    constructor(scene, config, mode) {
        super(scene, config, mode);
        this.bars = [];
        this.values = [Math.sqrt(2), Math.sqrt(5), Math.sqrt(8), Math.sqrt(17)]; // Example values
        this.labels = ['√2', '√5', '√8', '√17'];
    }

    init() {
        // Add lighting
        this.addLighting();

        // Add grid
        const gridHelper = new THREE.GridHelper(10, 10, 0x444444, 0x222222);
        this.addObject(gridHelper);

        // Create bars
        this.createBars();
    }

    createBars() {
        const barWidth = 0.8;
        const spacing = 1.5;
        const maxValue = Math.max(...this.values);
        const scale = 3; // Scale factor for visualization

        this.values.forEach((value, index) => {
            const height = (value / maxValue) * scale;
            const x = (index - this.values.length / 2) * spacing;

            // Bar geometry
            const barGeometry = new THREE.BoxGeometry(barWidth, height, barWidth);
            const barMaterial = new THREE.MeshStandardMaterial({
                color: this.getColorForIndex(index),
                metalness: 0.3,
                roughness: 0.7
            });
            const bar = new THREE.Mesh(barGeometry, barMaterial);
            bar.position.set(x, height / 2, 0);
            bar.castShadow = true;
            bar.receiveShadow = true;
            this.addObject(bar);
            this.bars.push(bar);

            // Label
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.width = 128;
            canvas.height = 64;
            context.fillStyle = 'white';
            context.font = 'bold 18px Arial';
            context.textAlign = 'center';
            context.fillText(this.labels[index], 64, 30);
            context.fillText(value.toFixed(2), 64, 50);

            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
            const label = new THREE.Sprite(spriteMaterial);
            label.position.set(x, height + 0.5, 0);
            label.scale.set(1, 0.5, 1);
            this.addObject(label);
        });

        // Add comparison lines if enabled
        if (this.config.show_comparison_lines) {
            this.addComparisonLines();
        }
    }

    addComparisonLines() {
        // Add horizontal lines connecting bars for easier comparison
        const lineMaterial = new THREE.LineBasicMaterial({
            color: 0xffff00,
            transparent: true,
            opacity: 0.3
        });

        // Connect tops of bars
        for (let i = 0; i < this.bars.length - 1; i++) {
            const pos1 = this.bars[i].position;
            const pos2 = this.bars[i + 1].position;
            const height1 = this.bars[i].geometry.parameters.height;
            const height2 = this.bars[i + 1].geometry.parameters.height;

            const lineGeometry = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(pos1.x, height1, 0),
                new THREE.Vector3(pos2.x, height2, 0)
            ]);
            const line = new THREE.Line(lineGeometry, lineMaterial);
            this.addObject(line);
        }
    }

    getColorForIndex(index) {
        const colors = [0xff6b6b, 0x4ecdc4, 0x45b7d1, 0xf9ca24, 0x6c5ce7];
        return colors[index % colors.length];
    }

    update() {
        // Animate bars if in full mode
        if (this.mode === 'full') {
            this.bars.forEach((bar, index) => {
                bar.rotation.y += 0.01 * (index + 1);
            });
        }
    }
}

