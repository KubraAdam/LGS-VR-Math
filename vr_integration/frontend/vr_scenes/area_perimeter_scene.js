/**
 * Area-Perimeter Scene
 * 3D shape with colored perimeter path and area fill
 */

import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { BaseScene } from './base_scene.js';

export class AreaPerimeterScene extends BaseScene {
    constructor(scene, config, mode) {
        super(scene, config, mode);
        this.shape = null;
        this.perimeterPath = null;
        this.areaFill = null;
        this.size = 4; // Default size
    }

    init() {
        // Add lighting
        this.addLighting();

        // Add grid
        const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
        this.addObject(gridHelper);

        // Create shape
        this.createShape();
    }

    createShape() {
        // Create square shape
        const geometry = new THREE.BoxGeometry(this.size, 0.1, this.size);
        
        // Area fill material
        const areaMaterial = new THREE.MeshStandardMaterial({
            color: this.hexToColor(this.config.area_color || '#0000ff'),
            transparent: true,
            opacity: 0.5,
            side: THREE.DoubleSide
        });
        
        this.areaFill = new THREE.Mesh(geometry, areaMaterial);
        this.areaFill.position.y = 0.05;
        this.areaFill.receiveShadow = true;
        this.addObject(this.areaFill);

        // Perimeter path (edges)
        if (this.config.show_perimeter_path) {
            this.createPerimeterPath();
        }

        // Add labels
        this.addLabels();
    }

    createPerimeterPath() {
        const perimeterColor = this.hexToColor(this.config.perimeter_color || '#00ff00');
        const halfSize = this.size / 2;
        const height = 0.2;

        // Create perimeter line (square path)
        const points = [
            new THREE.Vector3(-halfSize, height, -halfSize),
            new THREE.Vector3(halfSize, height, -halfSize),
            new THREE.Vector3(halfSize, height, halfSize),
            new THREE.Vector3(-halfSize, height, halfSize),
            new THREE.Vector3(-halfSize, height, -halfSize) // Close the loop
        ];

        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: perimeterColor,
            linewidth: 5
        });
        
        this.perimeterPath = new THREE.Line(geometry, material);
        this.addObject(this.perimeterPath);

        // Add animated point traveling along perimeter
        if (this.mode === 'guided' || this.mode === 'full') {
            this.addAnimatedPoint();
        }
    }

    addAnimatedPoint() {
        const pointGeometry = new THREE.SphereGeometry(0.15, 16, 16);
        const pointMaterial = new THREE.MeshBasicMaterial({
            color: 0xffff00,
            emissive: 0xffff00,
            emissiveIntensity: 1.0
        });
        this.animatedPoint = new THREE.Mesh(pointGeometry, pointMaterial);
        this.animatedPoint.position.set(-this.size / 2, 0.2, -this.size / 2);
        this.addObject(this.animatedPoint);
        this.animationProgress = 0;
    }

    addLabels() {
        const area = this.size * this.size;
        const perimeter = this.size * 4;

        // Area label
        const areaCanvas = document.createElement('canvas');
        const areaContext = areaCanvas.getContext('2d');
        areaCanvas.width = 256;
        areaCanvas.height = 64;
        areaContext.fillStyle = '#0000ff';
        areaContext.font = 'bold 20px Arial';
        areaContext.textAlign = 'center';
        areaContext.fillText(`Alan: ${area} cm²`, 128, 35);
        areaContext.fillText(`Çevre: ${perimeter} cm`, 128, 55);

        const areaTexture = new THREE.CanvasTexture(areaCanvas);
        const areaSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: areaTexture }));
        areaSprite.position.set(0, 3, 0);
        areaSprite.scale.set(2, 0.5, 1);
        this.addObject(areaSprite);

        // Edge labels with √ notation
        if (this.config.sqrt_edge_labels) {
            const edgeLabel = `Kenar: √${this.size * this.size} = ${this.size} cm`;
            const labelCanvas = document.createElement('canvas');
            const labelContext = labelCanvas.getContext('2d');
            labelCanvas.width = 256;
            labelCanvas.height = 32;
            labelContext.fillStyle = 'white';
            labelContext.font = '16px Arial';
            labelContext.textAlign = 'center';
            labelContext.fillText(edgeLabel, 128, 20);

            const labelTexture = new THREE.CanvasTexture(labelCanvas);
            const labelSprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: labelTexture }));
            labelSprite.position.set(0, 1, 0);
            labelSprite.scale.set(2, 0.3, 1);
            this.addObject(labelSprite);
        }
    }

    hexToColor(hex) {
        return parseInt(hex.replace('#', ''), 16);
    }

    update() {
        // Animate perimeter point
        if (this.animatedPoint && (this.mode === 'guided' || this.mode === 'full')) {
            this.animationProgress += 0.01;
            if (this.animationProgress > 1) this.animationProgress = 0;

            const halfSize = this.size / 2;
            let x, z;

            // Travel along perimeter
            if (this.animationProgress < 0.25) {
                // Bottom edge
                x = -halfSize + (this.animationProgress * 4) * this.size;
                z = -halfSize;
            } else if (this.animationProgress < 0.5) {
                // Right edge
                x = halfSize;
                z = -halfSize + ((this.animationProgress - 0.25) * 4) * this.size;
            } else if (this.animationProgress < 0.75) {
                // Top edge
                x = halfSize - ((this.animationProgress - 0.5) * 4) * this.size;
                z = halfSize;
            } else {
                // Left edge
                x = -halfSize;
                z = halfSize - ((this.animationProgress - 0.75) * 4) * this.size;
            }

            this.animatedPoint.position.set(x, 0.2, z);
        }
    }
}

