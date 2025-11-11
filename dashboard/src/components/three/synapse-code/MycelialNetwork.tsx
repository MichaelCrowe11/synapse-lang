'use client';

import { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { LSystem, detectAnastomosis, mycelialConfig } from '@/lib/lSystem';

interface MycelialNetworkProps {
  iterations?: number;
  biolumColor?: THREE.Color;
  amberColor?: THREE.Color;
  growthSpeed?: number;
  showAnastomosis?: boolean;
}

export function MycelialNetwork({
  iterations = 4,
  biolumColor = new THREE.Color('#00ffd9'),
  amberColor = new THREE.Color('#ffaa00'),
  growthSpeed = 0.5,
  showAnastomosis = true,
}: MycelialNetworkProps) {
  const hyphaeRef = useRef<THREE.LineSegments>(null);
  const anastomosisRef = useRef<THREE.LineSegments>(null);
  const [growthProgress, setGrowthProgress] = useState(0);

  // Generate mycelial network using L-system
  const { geometry, anastomosisGeometry, allPoints } = useMemo(() => {
    const lSystem = new LSystem({
      ...mycelialConfig,
      iterations,
    });

    const geo = lSystem.createGeometry();
    const positions = geo.attributes.position.array as Float32Array;

    // Extract points for anastomosis detection
    const points: THREE.Vector3[] = [];
    for (let i = 0; i < positions.length; i += 3) {
      points.push(new THREE.Vector3(positions[i], positions[i + 1], positions[i + 2]));
    }

    // Detect anastomosis (hyphal fusion)
    const anastomosisConnections = showAnastomosis ? detectAnastomosis(points, 0.6) : [];

    // Create anastomosis geometry
    const anastomosisPoints: number[] = [];
    anastomosisConnections.forEach(([i, j]) => {
      anastomosisPoints.push(
        points[i].x, points[i].y, points[i].z,
        points[j].x, points[j].y, points[j].z
      );
    });

    const anastGeo = new THREE.BufferGeometry();
    if (anastomosisPoints.length > 0) {
      anastGeo.setAttribute('position', new THREE.Float32BufferAttribute(anastomosisPoints, 3));
    }

    // Add colors to hyphae (gradient from base to tips)
    const colors: number[] = [];
    for (let i = 0; i < positions.length / 3; i++) {
      const t = i / (positions.length / 3);
      const color = amberColor.clone().lerp(biolumColor, t);
      colors.push(color.r, color.g, color.b);
    }
    geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return { geometry: geo, anastomosisGeometry: anastGeo, allPoints: points };
  }, [iterations, showAnastomosis, biolumColor, amberColor]);

  // Animate growth
  useFrame((state, delta) => {
    setGrowthProgress(prev => {
      const next = prev + delta * growthSpeed;
      return next > 1 ? 1 : next;
    });

    // Gentle organic movement
    if (hyphaeRef.current) {
      const time = state.clock.elapsedTime;
      hyphaeRef.current.rotation.y = Math.sin(time * 0.2) * 0.1;
      hyphaeRef.current.position.y = Math.sin(time * 0.3) * 0.05;
    }

    // Update growth visibility
    if (hyphaeRef.current && geometry) {
      const positions = geometry.attributes.position.array as Float32Array;
      const visibleCount = Math.floor((positions.length / 3) * growthProgress);

      // Create a new geometry with only visible segments
      const visiblePositions = positions.slice(0, visibleCount * 3);
      const newGeo = new THREE.BufferGeometry();
      newGeo.setAttribute('position', new THREE.Float32BufferAttribute(visiblePositions, 3));

      // Copy colors
      const colors = geometry.attributes.color.array as Float32Array;
      const visibleColors = colors.slice(0, visibleCount * 3);
      newGeo.setAttribute('color', new THREE.Float32BufferAttribute(visibleColors, 3));

      hyphaeRef.current.geometry.dispose();
      hyphaeRef.current.geometry = newGeo;
    }
  });

  // Create bioluminescent pulse effect along hyphae
  const pulseUniforms = useMemo(() => ({
    time: { value: 0 },
    biolumColor: { value: biolumColor },
    pulseSpeed: { value: 2.0 },
  }), [biolumColor]);

  useFrame((state) => {
    pulseUniforms.time.value = state.clock.elapsedTime;
  });

  return (
    <group>
      {/* Main hyphal network */}
      <lineSegments ref={hyphaeRef} geometry={geometry}>
        <lineBasicMaterial
          vertexColors
          transparent
          opacity={0.8}
          linewidth={2}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>

      {/* Anastomosis connections (hyphal fusion) */}
      {showAnastomosis && anastomosisGeometry && (
        <lineSegments ref={anastomosisRef} geometry={anastomosisGeometry}>
          <lineBasicMaterial
            color={biolumColor}
            transparent
            opacity={0.6 * growthProgress}
            linewidth={1.5}
            blending={THREE.AdditiveBlending}
          />
        </lineSegments>
      )}

      {/* Growth points (hyphal tips) */}
      <points>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[new Float32Array(allPoints.flatMap(p => [p.x, p.y, p.z])), 3]}
          />
        </bufferGeometry>
        <pointsMaterial
          size={0.08}
          color={biolumColor}
          transparent
          opacity={0.9 * growthProgress}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  );
}
