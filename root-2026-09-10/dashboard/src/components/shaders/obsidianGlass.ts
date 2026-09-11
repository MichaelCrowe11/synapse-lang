/**
 * Obsidian Glass Shader for Crowe Code
 * High-contrast, sharp, reflective with circuit-like reflections
 */

export const obsidianGlassVertex = `
varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;
varying vec3 vWorldPosition;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);

  vec4 worldPos = modelMatrix * vec4(position, 1.0);
  vWorldPosition = worldPos.xyz;

  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vPosition = mvPosition.xyz;

  gl_Position = projectionMatrix * mvPosition;
}
`;

export const obsidianGlassFragment = `
uniform float time;
uniform samplerCube envMap;
uniform vec3 electricColor; // Electric blue (#00d9ff)
uniform vec3 plasmaColor;   // Plasma purple (#6b00ff)
uniform float circuitIntensity;

varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;
varying vec3 vWorldPosition;

// Pseudo-random function for circuit patterns
float random(vec2 st) {
  return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

// Circuit pattern generator
float circuitPattern(vec2 p) {
  // Grid-based circuit lines
  vec2 grid = fract(p * 10.0);
  float lines = step(0.9, grid.x) + step(0.9, grid.y);

  // Random circuit nodes
  vec2 cellId = floor(p * 10.0);
  float nodeRandom = random(cellId);
  float nodes = step(0.95, nodeRandom) * (0.5 + 0.5 * sin(time * 3.0 + nodeRandom * 10.0));

  return lines * 0.3 + nodes;
}

void main() {
  vec3 viewDir = normalize(cameraPosition - vWorldPosition);
  vec3 normal = normalize(vNormal);

  // Sharp fresnel for obsidian (high power = sharp edge)
  float fresnel = pow(1.0 - dot(viewDir, normal), 5.0);

  // Minimal refraction (dark glass effect)
  vec3 refracted = refract(-viewDir, normal, 0.95);
  vec4 envColor = textureCube(envMap, refracted);

  // Strong reflection
  vec3 reflected = reflect(-viewDir, normal);
  vec4 reflColor = textureCube(envMap, reflected);

  // Circuit-like reflections
  vec2 circuitCoords = vWorldPosition.xy + vWorldPosition.z * 0.1;
  float circuit = circuitPattern(circuitCoords + time * 0.1);
  vec3 circuitColor = mix(plasmaColor, electricColor, circuit) * circuit * circuitIntensity;

  // High contrast composition
  vec3 baseColor = envColor.rgb * 0.2; // Very dark base
  vec3 reflectionColor = reflColor.rgb * 0.5;
  vec3 fresnelGlow = electricColor * fresnel * 0.8;

  vec3 finalColor = baseColor + reflectionColor + circuitColor + fresnelGlow;

  // High opacity for solid obsidian feel
  float alpha = 0.95;

  gl_FragColor = vec4(finalColor, alpha);
}
`;
