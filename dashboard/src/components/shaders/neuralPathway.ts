/**
 * Neural Pathway Shader for Crowe Code
 * Renders electric connections between neural nodes with traveling pulses
 */

export const neuralPathwayVertex = `
attribute vec3 position;
attribute vec3 target;
attribute float signal; // 0.0-1.0 activation level
attribute float pulseOffset;

uniform float time;
uniform mat4 modelViewMatrix;
uniform mat4 projectionMatrix;

varying float vSignal;
varying float vPulse;
varying float vDistance;

// Bezier curve for natural connection paths
vec3 bezier(vec3 a, vec3 b, vec3 control, float t) {
  float t2 = t * t;
  float oneMinusT = 1.0 - t;
  float oneMinusT2 = oneMinusT * oneMinusT;

  return oneMinusT2 * a + 2.0 * oneMinusT * t * control + t2 * b;
}

void main() {
  // Control point creates curve above midpoint
  vec3 midpoint = (position + target) * 0.5;
  vec3 control = midpoint + vec3(0.0, 2.0, 0.0);

  // Calculate position along bezier curve
  vec3 curvePos = bezier(position, target, control, signal);

  // Electric pulse animation traveling along path
  float pulseTime = time * 5.0 + pulseOffset;
  float pulse = sin(signal * 10.0 - pulseTime) * 0.5 + 0.5;
  vPulse = pow(pulse, 3.0); // Sharp pulse

  vSignal = signal;
  vDistance = length(target - position);

  vec4 mvPosition = modelViewMatrix * vec4(curvePos, 1.0);
  gl_Position = projectionMatrix * mvPosition;

  // Point size for line rendering
  gl_PointSize = 2.0 + vPulse * 3.0;
}
`;

export const neuralPathwayFragment = `
uniform vec3 activeColor;   // Electric blue (#00d9ff)
uniform vec3 inactiveColor; // Deep purple (#6b00ff)
uniform float glowIntensity;

varying float vSignal;
varying float vPulse;
varying float vDistance;

void main() {
  // Color based on activation level
  vec3 baseColor = mix(inactiveColor, activeColor, vSignal);

  // Pulse glow effect
  float glow = vPulse * glowIntensity;

  // Distance fade (farther connections are dimmer)
  float distanceFade = 1.0 - clamp(vDistance / 20.0, 0.0, 0.7);

  vec3 finalColor = baseColor * (1.0 + glow * 2.0) * distanceFade;

  // Opacity based on activation and pulse
  float alpha = (0.4 + vSignal * 0.4 + vPulse * 0.2) * distanceFade;

  gl_FragColor = vec4(finalColor, alpha);
}
`;
