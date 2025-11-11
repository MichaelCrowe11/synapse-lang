/**
 * Organic Glass Shader for Synapse-Code
 * Soft, translucent, organic flow with subsurface scattering
 */

export const organicGlassVertex = `
varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;
varying vec3 vWorldPosition;
varying vec3 vViewPosition;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);

  vec4 worldPos = modelMatrix * vec4(position, 1.0);
  vWorldPosition = worldPos.xyz;

  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vPosition = mvPosition.xyz;
  vViewPosition = -mvPosition.xyz;

  gl_Position = projectionMatrix * mvPosition;
}
`;

export const organicGlassFragment = `
uniform float time;
uniform samplerCube envMap;
uniform sampler2D noiseTexture;
uniform vec3 biolumColor;     // Bioluminescent teal (#00ffd9)
uniform vec3 amberColor;       // Fungal amber (#ffaa00)
uniform vec3 lightPosition;
uniform float subsurfaceStrength;
uniform float flowSpeed;

varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;
varying vec3 vWorldPosition;
varying vec3 vViewPosition;

// Simplex-style noise approximation (for organic flow)
float noise(vec2 p) {
  return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float fbm(vec2 p) {
  float value = 0.0;
  float amplitude = 0.5;
  for(int i = 0; i < 4; i++) {
    value += amplitude * noise(p);
    p *= 2.0;
    amplitude *= 0.5;
  }
  return value;
}

void main() {
  vec3 viewDir = normalize(vViewPosition);
  vec3 lightDir = normalize(lightPosition - vWorldPosition);
  vec3 normal = normalize(vNormal);

  // Organic flow texture
  vec2 flowUV = vUv + time * flowSpeed;
  float flow1 = fbm(flowUV * 2.0);
  float flow2 = fbm(flowUV * 3.0 + 0.5);
  float flowPattern = (flow1 + flow2) * 0.5;

  // Perturb normal with organic flow
  vec3 flowNormal = normalize(normal + vec3(
    (flow1 - 0.5) * 0.3,
    (flow2 - 0.5) * 0.3,
    0.0
  ));

  // Soft fresnel for organic glass
  float fresnel = pow(1.0 - max(dot(viewDir, flowNormal), 0.0), 2.5);

  // Multiple refractions for subsurface scattering effect
  vec3 refract1 = refract(-viewDir, flowNormal, 0.98);
  vec3 refract2 = refract(-viewDir, flowNormal, 0.96);
  vec3 refract3 = refract(-viewDir, flowNormal, 0.94);

  vec4 env1 = textureCube(envMap, refract1);
  vec4 env2 = textureCube(envMap, refract2);
  vec4 env3 = textureCube(envMap, refract3);

  // Blend refractions for depth (subsurface effect)
  vec3 refraction = (env1.rgb + env2.rgb * 1.2 + env3.rgb * 0.8) / 3.0;

  // Subsurface scattering (light passing through)
  float thickness = 0.5 + flowPattern * 0.5;
  float scatter = pow(max(0.0, dot(-lightDir, flowNormal)), 2.0) * (1.0 - thickness);
  vec3 subsurface = amberColor * scatter * subsurfaceStrength;

  // Bioluminescent glow based on flow pattern
  vec3 bioGlow = biolumColor * flowPattern * 0.4;

  // Soft fresnel rim
  vec3 fresnelColor = mix(biolumColor, amberColor, 0.5) * fresnel * 0.5;

  // Combine all organic elements
  vec3 finalColor = refraction * 0.6 + subsurface + bioGlow + fresnelColor;

  // Variable opacity based on flow (creates organic depth)
  float alpha = 0.85 + flowPattern * 0.15;

  gl_FragColor = vec4(finalColor, alpha);
}
`;
