'use client';

import { Scene } from '@/components/three/shared/Scene';
import { MycelialNetwork } from '@/components/three/synapse-code/MycelialNetwork';
import { OrganicGlassMaterial } from '@/components/three/shared/OrganicGlassMaterial';
import * as THREE from 'three';

export function SynapseCodeScene() {
  return (
    <>
      {/* Title overlay */}
      <div className="absolute top-0 left-0 right-0 z-10 p-8">
        <h1 className="text-6xl font-bold bg-gradient-to-r from-teal-400 via-amber-400 to-teal-300 bg-clip-text text-transparent">
          SYNAPSE-CODE
        </h1>
        <p className="text-teal-300 text-xl mt-2">Fungal Intelligence, Evolved</p>
      </div>

      {/* Brand description */}
      <div className="absolute bottom-0 left-0 right-0 z-10 p-8 bg-gradient-to-t from-black/80 to-transparent">
        <div className="max-w-2xl">
          <h2 className="text-2xl font-bold text-teal-400 mb-3">Mycelial Code Networks</h2>
          <p className="text-gray-300 leading-relaxed">
            Synapse-Code grew from a simple observation: fungal networks solved complex problems
            millions of years before computers existed. By encoding these biological principles
            into our framework, we've created code that doesn't just run—it grows, adapts, and
            evolves like living intelligence.
          </p>
          <div className="mt-4 flex gap-4">
            <button className="px-6 py-3 bg-teal-500 hover:bg-teal-400 text-black font-semibold rounded-lg transition-colors">
              Grow Your Code
            </button>
            <button className="px-6 py-3 bg-amber-600 hover:bg-amber-500 text-white font-semibold rounded-lg transition-colors">
              Learn Biology
            </button>
          </div>
        </div>
      </div>

      {/* 3D Scene */}
      <Scene
        backgroundColor="#0f0a0a"
        cameraPosition={[0, 3, 15]}
        fog={{ color: '#1a1410', near: 10, far: 40 }}
      >
        {/* Mycelial Network Visualization */}
        <MycelialNetwork
          iterations={5}
          biolumColor={new THREE.Color('#00ffd9')}
          amberColor={new THREE.Color('#ffaa00')}
          growthSpeed={0.3}
          showAnastomosis={true}
        />

        {/* Organic Glass Orbs with mycelial content */}
        <group position={[-3, 2, -2]}>
          <mesh>
            <sphereGeometry args={[0.8, 32, 32]} />
            <OrganicGlassMaterial
              biolumColor={new THREE.Color('#00ffd9')}
              amberColor={new THREE.Color('#ffaa00')}
              subsurfaceStrength={0.7}
              flowSpeed={0.03}
              lightPosition={new THREE.Vector3(5, 5, 5)}
            />
          </mesh>
        </group>

        <group position={[4, -1, -1]}>
          <mesh>
            <sphereGeometry args={[1.0, 32, 32]} />
            <OrganicGlassMaterial
              biolumColor={new THREE.Color('#00ffd9')}
              amberColor={new THREE.Color('#ffaa00')}
              subsurfaceStrength={0.6}
              flowSpeed={0.04}
              lightPosition={new THREE.Vector3(5, 5, 5)}
            />
          </mesh>
        </group>

        <group position={[2, 3, -3]}>
          <mesh>
            <sphereGeometry args={[0.6, 32, 32]} />
            <OrganicGlassMaterial
              biolumColor={new THREE.Color('#00ffd9')}
              amberColor={new THREE.Color('#ffaa00')}
              subsurfaceStrength={0.8}
              flowSpeed={0.02}
              lightPosition={new THREE.Vector3(5, 5, 5)}
            />
          </mesh>
        </group>

        {/* Bioluminescent lighting */}
        <pointLight position={[0, 5, 2]} intensity={1.5} color="#00ffd9" />
        <pointLight position={[-5, 0, -3]} intensity={0.8} color="#ffaa00" />
        <pointLight position={[5, -3, 0]} intensity={0.6} color="#00ffd9" />

        {/* Ambient adjustment for organic feel */}
        <ambientLight intensity={0.15} color="#ffaa00" />
      </Scene>

      {/* Organic texture overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-5"
        style={{
          backgroundImage: `radial-gradient(circle at 20% 50%, #00ffd9 1px, transparent 1px),
                           radial-gradient(circle at 80% 20%, #ffaa00 1px, transparent 1px),
                           radial-gradient(circle at 40% 80%, #00ffd9 1px, transparent 1px)`,
          backgroundSize: '100px 100px, 150px 150px, 80px 80px'
        }}
      />
    </>
  );
}
