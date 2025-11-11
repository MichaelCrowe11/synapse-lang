'use client';

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { organicGlassVertex, organicGlassFragment } from '@/components/shaders/organicGlass';

interface OrganicGlassMaterialProps {
  biolumColor?: THREE.Color;
  amberColor?: THREE.Color;
  subsurfaceStrength?: number;
  flowSpeed?: number;
  lightPosition?: THREE.Vector3;
  envMap?: THREE.CubeTexture;
  noiseTexture?: THREE.Texture;
}

export function OrganicGlassMaterial({
  biolumColor = new THREE.Color('#00ffd9'),
  amberColor = new THREE.Color('#ffaa00'),
  subsurfaceStrength = 0.5,
  flowSpeed = 0.03,
  lightPosition = new THREE.Vector3(5, 5, 5),
  envMap,
  noiseTexture,
}: OrganicGlassMaterialProps) {
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const uniforms = useMemo(
    () => ({
      time: { value: 0 },
      envMap: { value: envMap || null },
      noiseTexture: { value: noiseTexture || null },
      biolumColor: { value: biolumColor },
      amberColor: { value: amberColor },
      lightPosition: { value: lightPosition },
      subsurfaceStrength: { value: subsurfaceStrength },
      flowSpeed: { value: flowSpeed },
    }),
    [biolumColor, amberColor, lightPosition, subsurfaceStrength, flowSpeed, envMap, noiseTexture]
  );

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.time.value = state.clock.elapsedTime;
    }
  });

  return (
    <shaderMaterial
      ref={materialRef}
      vertexShader={organicGlassVertex}
      fragmentShader={organicGlassFragment}
      uniforms={uniforms}
      transparent
      side={THREE.DoubleSide}
    />
  );
}
