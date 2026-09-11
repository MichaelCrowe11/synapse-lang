'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { obsidianGlassVertex, obsidianGlassFragment } from '@/components/shaders/obsidianGlass';

interface ObsidianGlassMaterialProps {
  electricColor?: THREE.Color;
  plasmaColor?: THREE.Color;
  circuitIntensity?: number;
  envMap?: THREE.CubeTexture;
}

export function ObsidianGlassMaterial({
  electricColor = new THREE.Color('#00d9ff'),
  plasmaColor = new THREE.Color('#6b00ff'),
  circuitIntensity = 0.5,
  envMap,
}: ObsidianGlassMaterialProps) {
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      time: { value: 0 },
      envMap: { value: envMap || null },
      electricColor: { value: electricColor },
      plasmaColor: { value: plasmaColor },
      circuitIntensity: { value: circuitIntensity },
    }),
    [electricColor, plasmaColor, circuitIntensity, envMap]
  );

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.time.value = state.clock.elapsedTime;
    }
  });

  return (
    <shaderMaterial
      ref={materialRef}
      vertexShader={obsidianGlassVertex}
      fragmentShader={obsidianGlassFragment}
      uniforms={uniforms}
      transparent
      side={THREE.DoubleSide}
    />
  );
}
