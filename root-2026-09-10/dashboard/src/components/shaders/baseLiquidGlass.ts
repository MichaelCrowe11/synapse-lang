/**
 * Base Liquid Glass Shader
 * Shared foundation for both Crowe Code (obsidian) and Synapse-Code (organic) glass materials
 */

export const baseLiquidGlassVertex = `
varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;
varying vec3 vViewPosition;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);

  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vPosition = mvPosition.xyz;
  vViewPosition = -mvPosition.xyz;

  gl_Position = projectionMatrix * mvPosition;
}
`;

export const baseLiquidGlassFragment = `
uniform float time;
uniform float opacity;
uniform vec3 color;
uniform float fresnelPower;
uniform float refractionRatio;
uniform samplerCube envMap;

varying vec3 vNormal;
varying vec3 vPosition;
varying vec2 vUv;
varying vec3 vViewPosition;

void main() {
  vec3 viewDir = normalize(vViewPosition);
  vec3 normal = normalize(vNormal);

  // Fresnel effect
  float fresnel = pow(1.0 - max(dot(viewDir, normal), 0.0), fresnelPower);

  // Basic refraction
  vec3 refracted = refract(-viewDir, normal, refractionRatio);
  vec4 envColor = textureCube(envMap, refracted);

  // Basic reflection
  vec3 reflected = reflect(-viewDir, normal);
  vec4 reflColor = textureCube(envMap, reflected);

  // Combine
  vec3 finalColor = mix(envColor.rgb, reflColor.rgb, fresnel) * color;

  gl_FragColor = vec4(finalColor, opacity);
}
`;
