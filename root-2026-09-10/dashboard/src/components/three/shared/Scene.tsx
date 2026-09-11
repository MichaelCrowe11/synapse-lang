'use client';

import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment } from '@react-three/drei';
import { ReactNode, Suspense } from 'react';

interface SceneProps {
  children: ReactNode;
  backgroundColor?: string;
  cameraPosition?: [number, number, number];
  enableControls?: boolean;
  fog?: { color: string; near: number; far: number };
}

export function Scene({
  children,
  backgroundColor = '#0a0a0f',
  cameraPosition = [0, 0, 15],
  enableControls = true,
  fog,
}: SceneProps) {
  return (
    <div className="w-full h-screen">
      <Canvas
        camera={{ position: cameraPosition, fov: 45 }}
        gl={{
          alpha: true,
          antialias: true,
          powerPreference: 'high-performance',
        }}
      >
        {/* Background color */}
        <color attach="background" args={[backgroundColor]} />

        {/* Fog (optional) */}
        {fog && <fog attach="fog" args={[fog.color, fog.near, fog.far]} />}

        {/* Lighting */}
        <ambientLight intensity={0.2} color="#2244ff" />
        <directionalLight position={[5, 5, 5]} intensity={0.5} color="#00d9ff" />
        <directionalLight position={[-5, -5, -5]} intensity={0.3} color="#6b00ff" />

        {/* Environment map for reflections */}
        <Suspense fallback={null}>
          <Environment preset="city" />
        </Suspense>

        {/* Scene content */}
        <Suspense fallback={null}>
          {children}
        </Suspense>

        {/* Controls */}
        {enableControls && (
          <OrbitControls
            enableZoom={true}
            enablePan={true}
            enableRotate={true}
            maxDistance={30}
            minDistance={5}
          />
        )}
      </Canvas>
    </div>
  );
}
