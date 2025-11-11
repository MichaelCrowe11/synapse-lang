'use client';

import { Scene } from '@/components/three/shared/Scene';
import { NeuralNetwork } from '@/components/three/crowe-code/NeuralNetwork';
import { ObsidianGlassMaterial } from '@/components/three/shared/ObsidianGlassMaterial';
import * as THREE from 'three';

export function CroweCodeScene() {
  return (
    <>
      {/* Title overlay */}
      <div className="absolute top-0 left-0 right-0 z-10 p-8">
        <h1 className="text-6xl font-bold bg-gradient-to-r from-cyan-400 to-purple-600 bg-clip-text text-transparent">
          CROWE CODE
        </h1>
        <p className="text-cyan-300 text-xl mt-2">Where AI Meets Code Intelligence</p>
      </div>

      {/* Brand description */}
      <div className="absolute bottom-0 left-0 right-0 z-10 p-8 bg-gradient-to-t from-black/80 to-transparent">
        <div className="max-w-2xl">
          <h2 className="text-2xl font-bold text-cyan-400 mb-3">Neural Code Intelligence</h2>
          <p className="text-gray-300 leading-relaxed">
            Powered by 150+ specialized AI agents working in harmony, Crowe Code doesn't just
            generate code—it understands your intent, learns from your patterns, and evolves
            with your projects. Experience the most sophisticated code intelligence platform
            ever built.
          </p>
          <div className="mt-4 flex gap-4">
            <button className="px-6 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-semibold rounded-lg transition-colors">
              Start Coding
            </button>
            <button className="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white font-semibold rounded-lg transition-colors">
              View Agents
            </button>
          </div>
        </div>
      </div>

      {/* 3D Scene */}
      <Scene
        backgroundColor="#0a0a0f"
        cameraPosition={[0, 0, 20]}
        fog={{ color: '#1a1a3e', near: 10, far: 50 }}
      >
        {/* Neural Network Visualization */}
        <NeuralNetwork
          nodeCount={150}
          layers={6}
          spread={12}
          activeColor={new THREE.Color('#00d9ff')}
          inactiveColor={new THREE.Color('#6b00ff')}
        />

        {/* Obsidian Glass Orbs */}
        <group position={[-4, 2, -2]}>
          <mesh>
            <sphereGeometry args={[0.8, 32, 32]} />
            <ObsidianGlassMaterial
              electricColor={new THREE.Color('#00d9ff')}
              plasmaColor={new THREE.Color('#6b00ff')}
              circuitIntensity={0.6}
            />
          </mesh>
        </group>

        <group position={[4, -2, -1]}>
          <mesh>
            <sphereGeometry args={[1.2, 32, 32]} />
            <ObsidianGlassMaterial
              electricColor={new THREE.Color('#00d9ff')}
              plasmaColor={new THREE.Color('#6b00ff')}
              circuitIntensity={0.7}
            />
          </mesh>
        </group>

        <group position={[0, 3, -3]}>
          <mesh>
            <sphereGeometry args={[0.6, 32, 32]} />
            <ObsidianGlassMaterial
              electricColor={new THREE.Color('#00d9ff')}
              plasmaColor={new THREE.Color('#6b00ff')}
              circuitIntensity={0.5}
            />
          </mesh>
        </group>

        {/* Additional lighting for dramatic effect */}
        <pointLight position={[0, 5, 5]} intensity={1} color="#00d9ff" />
        <pointLight position={[0, -5, -5]} intensity={0.5} color="#6b00ff" />
      </Scene>

      {/* Subtle grid background */}
      <div className="absolute inset-0 pointer-events-none opacity-10"
        style={{
          backgroundImage: `linear-gradient(#00d9ff 1px, transparent 1px),
                           linear-gradient(90deg, #00d9ff 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}
      />
    </>
  );
}
