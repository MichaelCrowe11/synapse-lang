/**
 * L-System Implementation for Organic Mycelial Growth
 * Based on Lindenmayer systems for natural branching patterns
 */

import * as THREE from 'three';

export interface LSystemConfig {
  axiom: string;
  rules: Record<string, string>;
  angle: number;          // Branch angle in degrees
  length: number;         // Segment length
  lengthScale: number;    // Length reduction per iteration
  iterations: number;
}

export interface TurtleState {
  position: THREE.Vector3;
  direction: THREE.Vector3;
  right: THREE.Vector3;
  up: THREE.Vector3;
}

// Default mycelial growth configuration
export const mycelialConfig: LSystemConfig = {
  axiom: 'F',
  rules: {
    'F': 'F[+F]F[-F][F]',  // Branch pattern: forward, branch right, forward, branch left, forward
    'X': 'F-[[X]+X]+F[+FX]-X', // Complex branching
  },
  angle: 25,
  length: 0.3,
  lengthScale: 0.85,
  iterations: 4,
};

export class LSystem {
  private config: LSystemConfig;

  constructor(config: LSystemConfig = mycelialConfig) {
    this.config = config;
  }

  /**
   * Generate L-system string by applying rules iteratively
   */
  generate(iterations?: number): string {
    let current = this.config.axiom;
    const maxIterations = iterations ?? this.config.iterations;

    for (let i = 0; i < maxIterations; i++) {
      current = this.applyRules(current);
    }

    return current;
  }

  /**
   * Apply production rules to string
   */
  private applyRules(input: string): string {
    let output = '';

    for (const char of input) {
      output += this.config.rules[char] ?? char;
    }

    return output;
  }

  /**
   * Create 3D geometry from L-system string using turtle graphics
   */
  createGeometry(instructions?: string, config?: Partial<LSystemConfig>): THREE.BufferGeometry {
    const mergedConfig = { ...this.config, ...config };
    const lSystemString = instructions ?? this.generate();

    const points: THREE.Vector3[] = [];
    const stateStack: TurtleState[] = [];

    // Initial turtle state
    let position = new THREE.Vector3(0, 0, 0);
    let direction = new THREE.Vector3(0, 1, 0);
    let right = new THREE.Vector3(1, 0, 0);
    let up = new THREE.Vector3(0, 0, 1);
    let currentLength = mergedConfig.length;

    const angleRad = (mergedConfig.angle * Math.PI) / 180;

    for (const char of lSystemString) {
      switch (char) {
        case 'F': // Move forward and draw
          {
            const start = position.clone();
            position = position.clone().add(direction.clone().multiplyScalar(currentLength));
            points.push(start, position);
          }
          break;

        case 'f': // Move forward without drawing
          position = position.clone().add(direction.clone().multiplyScalar(currentLength));
          break;

        case '+': // Rotate right (yaw)
          {
            const rotation = new THREE.Matrix4().makeRotationAxis(up, angleRad);
            direction.applyMatrix4(rotation).normalize();
            right.applyMatrix4(rotation).normalize();
          }
          break;

        case '-': // Rotate left (yaw)
          {
            const rotation = new THREE.Matrix4().makeRotationAxis(up, -angleRad);
            direction.applyMatrix4(rotation).normalize();
            right.applyMatrix4(rotation).normalize();
          }
          break;

        case '&': // Pitch down
          {
            const rotation = new THREE.Matrix4().makeRotationAxis(right, angleRad);
            direction.applyMatrix4(rotation).normalize();
            up.applyMatrix4(rotation).normalize();
          }
          break;

        case '^': // Pitch up
          {
            const rotation = new THREE.Matrix4().makeRotationAxis(right, -angleRad);
            direction.applyMatrix4(rotation).normalize();
            up.applyMatrix4(rotation).normalize();
          }
          break;

        case '\\': // Roll left
          {
            const rotation = new THREE.Matrix4().makeRotationAxis(direction, angleRad);
            right.applyMatrix4(rotation).normalize();
            up.applyMatrix4(rotation).normalize();
          }
          break;

        case '/': // Roll right
          {
            const rotation = new THREE.Matrix4().makeRotationAxis(direction, -angleRad);
            right.applyMatrix4(rotation).normalize();
            up.applyMatrix4(rotation).normalize();
          }
          break;

        case '[': // Push state (start branch)
          stateStack.push({
            position: position.clone(),
            direction: direction.clone(),
            right: right.clone(),
            up: up.clone(),
          });
          currentLength *= mergedConfig.lengthScale;
          break;

        case ']': // Pop state (end branch)
          {
            const state = stateStack.pop();
            if (state) {
              position = state.position;
              direction = state.direction;
              right = state.right;
              up = state.up;
            }
            currentLength /= mergedConfig.lengthScale;
          }
          break;

        default:
          // Ignore unknown characters
          break;
      }
    }

    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    return geometry;
  }

  /**
   * Create animated growth geometry (returns array of geometries at different growth stages)
   */
  createGrowthStages(stages: number = 10): THREE.BufferGeometry[] {
    const fullString = this.generate();
    const geometries: THREE.BufferGeometry[] = [];

    for (let i = 1; i <= stages; i++) {
      const length = Math.floor((fullString.length * i) / stages);
      const substring = fullString.substring(0, length);
      geometries.push(this.createGeometry(substring));
    }

    return geometries;
  }
}

/**
 * Anastomosis: Hyphal fusion detection and connection
 * When two hyphae tips come close, they fuse creating loops (biological accuracy)
 */
export function detectAnastomosis(
  points: THREE.Vector3[],
  threshold: number = 0.5
): [number, number][] {
  const connections: [number, number][] = [];

  for (let i = 0; i < points.length; i += 2) {
    for (let j = i + 4; j < points.length; j += 2) {
      const distance = points[i].distanceTo(points[j]);

      if (distance < threshold && distance > 0.01) {
        connections.push([i, j]);
      }
    }
  }

  return connections;
}
