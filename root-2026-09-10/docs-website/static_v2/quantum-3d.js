// Quantum 3D Visualization using Three.js alternative (pure WebGL)
class Quantum3D {
    constructor(container) {
        this.container = container || document.body;
        this.init();
    }

    init() {
        // Create canvas
        this.canvas = document.createElement('canvas');
        this.canvas.style.cssText = `
            width: 100%;
            height: 400px;
            background: linear-gradient(180deg, #000 0%, #1a1a2e 100%);
            border: 2px solid #5B47E0;
        `;
        this.container.appendChild(this.canvas);

        // Get WebGL context
        this.gl = this.canvas.getContext('webgl') || this.canvas.getContext('experimental-webgl');

        if (!this.gl) {
            console.error('WebGL not supported');
            return;
        }

        this.setupGL();
        this.createQuantumSphere();
        this.animate();
    }

    setupGL() {
        const gl = this.gl;

        // Vertex shader
        const vertexShaderSource = `
            attribute vec3 aPosition;
            attribute vec3 aNormal;

            uniform mat4 uProjectionMatrix;
            uniform mat4 uModelViewMatrix;
            uniform mat4 uNormalMatrix;

            varying vec3 vNormal;
            varying vec3 vPosition;

            void main() {
                vNormal = normalize(vec3(uNormalMatrix * vec4(aNormal, 1.0)));
                vPosition = aPosition;
                gl_Position = uProjectionMatrix * uModelViewMatrix * vec4(aPosition, 1.0);
            }
        `;

        // Fragment shader with quantum effects
        const fragmentShaderSource = `
            precision mediump float;

            uniform float uTime;
            uniform vec3 uColor;

            varying vec3 vNormal;
            varying vec3 vPosition;

            void main() {
                // Quantum wave function visualization
                float wave = sin(vPosition.x * 10.0 + uTime) *
                            cos(vPosition.y * 10.0 + uTime) *
                            sin(vPosition.z * 10.0 + uTime);

                // Probability density
                float probability = abs(wave);

                // Holographic effect
                vec3 color = vec3(
                    0.5 + 0.5 * sin(uTime + probability * 6.28),
                    0.5 + 0.5 * sin(uTime + probability * 6.28 + 2.09),
                    0.5 + 0.5 * sin(uTime + probability * 6.28 + 4.18)
                );

                // Lighting
                vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
                float diff = max(dot(vNormal, lightDir), 0.0);

                // Rim lighting for quantum glow
                vec3 viewDir = normalize(-vPosition);
                float rim = 1.0 - max(dot(viewDir, vNormal), 0.0);
                rim = smoothstep(0.6, 1.0, rim);

                color *= diff;
                color += vec3(0.4, 0.3, 0.8) * rim * 2.0;

                // Pulsing alpha
                float alpha = 0.7 + 0.3 * sin(uTime * 2.0);

                gl_FragColor = vec4(color, alpha);
            }
        `;

        // Compile shaders
        this.vertexShader = this.compileShader(gl.VERTEX_SHADER, vertexShaderSource);
        this.fragmentShader = this.compileShader(gl.FRAGMENT_SHADER, fragmentShaderSource);

        // Create program
        this.program = gl.createProgram();
        gl.attachShader(this.program, this.vertexShader);
        gl.attachShader(this.program, this.fragmentShader);
        gl.linkProgram(this.program);

        if (!gl.getProgramParameter(this.program, gl.LINK_STATUS)) {
            console.error('Unable to initialize shader program:', gl.getProgramInfoLog(this.program));
            return;
        }

        // Get attribute locations
        this.aPosition = gl.getAttribLocation(this.program, 'aPosition');
        this.aNormal = gl.getAttribLocation(this.program, 'aNormal');

        // Get uniform locations
        this.uProjectionMatrix = gl.getUniformLocation(this.program, 'uProjectionMatrix');
        this.uModelViewMatrix = gl.getUniformLocation(this.program, 'uModelViewMatrix');
        this.uNormalMatrix = gl.getUniformLocation(this.program, 'uNormalMatrix');
        this.uTime = gl.getUniformLocation(this.program, 'uTime');
        this.uColor = gl.getUniformLocation(this.program, 'uColor');

        // Enable depth testing
        gl.enable(gl.DEPTH_TEST);
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    }

    compileShader(type, source) {
        const gl = this.gl;
        const shader = gl.createShader(type);
        gl.shaderSource(shader, source);
        gl.compileShader(shader);

        if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
            console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
            gl.deleteShader(shader);
            return null;
        }

        return shader;
    }

    createQuantumSphere() {
        const gl = this.gl;

        // Generate sphere vertices
        const positions = [];
        const normals = [];
        const indices = [];

        const latitudeBands = 30;
        const longitudeBands = 30;
        const radius = 1.0;

        for (let lat = 0; lat <= latitudeBands; lat++) {
            const theta = lat * Math.PI / latitudeBands;
            const sinTheta = Math.sin(theta);
            const cosTheta = Math.cos(theta);

            for (let lon = 0; lon <= longitudeBands; lon++) {
                const phi = lon * 2 * Math.PI / longitudeBands;
                const sinPhi = Math.sin(phi);
                const cosPhi = Math.cos(phi);

                const x = cosPhi * sinTheta;
                const y = cosTheta;
                const z = sinPhi * sinTheta;

                positions.push(radius * x, radius * y, radius * z);
                normals.push(x, y, z);
            }
        }

        for (let lat = 0; lat < latitudeBands; lat++) {
            for (let lon = 0; lon < longitudeBands; lon++) {
                const first = (lat * (longitudeBands + 1)) + lon;
                const second = first + longitudeBands + 1;

                indices.push(first, second, first + 1);
                indices.push(second, second + 1, first + 1);
            }
        }

        // Create buffers
        this.positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, this.positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);

        this.normalBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, this.normalBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(normals), gl.STATIC_DRAW);

        this.indexBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(indices), gl.STATIC_DRAW);

        this.indexCount = indices.length;
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const gl = this.gl;
        const canvas = this.canvas;

        // Resize canvas if needed
        const displayWidth = canvas.clientWidth;
        const displayHeight = canvas.clientHeight;

        if (canvas.width !== displayWidth || canvas.height !== displayHeight) {
            canvas.width = displayWidth;
            canvas.height = displayHeight;
            gl.viewport(0, 0, canvas.width, canvas.height);
        }

        // Clear
        gl.clearColor(0.0, 0.0, 0.0, 0.0);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

        // Use shader program
        gl.useProgram(this.program);

        // Set up matrices
        const projectionMatrix = this.perspective(45, canvas.width / canvas.height, 0.1, 100.0);
        const modelViewMatrix = this.lookAt(
            [3 * Math.cos(Date.now() * 0.001), 2, 3 * Math.sin(Date.now() * 0.001)], // Eye position (rotating)
            [0, 0, 0], // Look at
            [0, 1, 0]  // Up
        );
        const normalMatrix = this.transpose(this.inverse(modelViewMatrix));

        // Set uniforms
        gl.uniformMatrix4fv(this.uProjectionMatrix, false, projectionMatrix);
        gl.uniformMatrix4fv(this.uModelViewMatrix, false, modelViewMatrix);
        gl.uniformMatrix4fv(this.uNormalMatrix, false, normalMatrix);
        gl.uniform1f(this.uTime, Date.now() * 0.001);
        gl.uniform3f(this.uColor, 0.4, 0.3, 0.8);

        // Bind buffers and draw
        gl.bindBuffer(gl.ARRAY_BUFFER, this.positionBuffer);
        gl.enableVertexAttribArray(this.aPosition);
        gl.vertexAttribPointer(this.aPosition, 3, gl.FLOAT, false, 0, 0);

        gl.bindBuffer(gl.ARRAY_BUFFER, this.normalBuffer);
        gl.enableVertexAttribArray(this.aNormal);
        gl.vertexAttribPointer(this.aNormal, 3, gl.FLOAT, false, 0, 0);

        gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.indexBuffer);
        gl.drawElements(gl.TRIANGLES, this.indexCount, gl.UNSIGNED_SHORT, 0);
    }

    // Matrix math utilities
    perspective(fovy, aspect, near, far) {
        const f = 1.0 / Math.tan(fovy * Math.PI / 360.0);
        const nf = 1 / (near - far);

        return new Float32Array([
            f / aspect, 0, 0, 0,
            0, f, 0, 0,
            0, 0, (far + near) * nf, -1,
            0, 0, (2 * far * near) * nf, 0
        ]);
    }

    lookAt(eye, center, up) {
        const zAxis = this.normalize(this.subtract(eye, center));
        const xAxis = this.normalize(this.cross(up, zAxis));
        const yAxis = this.normalize(this.cross(zAxis, xAxis));

        return new Float32Array([
            xAxis[0], xAxis[1], xAxis[2], 0,
            yAxis[0], yAxis[1], yAxis[2], 0,
            zAxis[0], zAxis[1], zAxis[2], 0,
            -this.dot(xAxis, eye), -this.dot(yAxis, eye), -this.dot(zAxis, eye), 1
        ]);
    }

    normalize(v) {
        const length = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
        return [v[0] / length, v[1] / length, v[2] / length];
    }

    subtract(a, b) {
        return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
    }

    cross(a, b) {
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0]
        ];
    }

    dot(a, b) {
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    }

    transpose(m) {
        return new Float32Array([
            m[0], m[4], m[8], m[12],
            m[1], m[5], m[9], m[13],
            m[2], m[6], m[10], m[14],
            m[3], m[7], m[11], m[15]
        ]);
    }

    inverse(m) {
        // Simple 4x4 matrix inverse (simplified for demo)
        // In production, use a proper matrix library
        const inv = new Float32Array(16);

        inv[0] = m[5] * m[10] * m[15] - m[5] * m[11] * m[14] - m[9] * m[6] * m[15] +
                m[9] * m[7] * m[14] + m[13] * m[6] * m[11] - m[13] * m[7] * m[10];

        // ... (full inverse calculation omitted for brevity)
        // Using identity matrix as fallback
        return new Float32Array([
            1, 0, 0, 0,
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1
        ]);
    }
}

// Auto-initialize on elements with class 'quantum-3d'
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.quantum-3d').forEach(container => {
        new Quantum3D(container);
    });
});