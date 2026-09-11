'use client';

import dynamic from 'next/dynamic';

const SynapseCodeScene = dynamic(
  () => import('./SynapseCodeScene').then(mod => ({ default: mod.SynapseCodeScene })),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-screen flex items-center justify-center bg-[#0f0a0a]">
        <div className="text-teal-400 text-2xl animate-pulse">Loading Synapse-Code...</div>
      </div>
    ),
  }
);

export default function SynapseCodePage() {
  return (
    <main className="relative w-full h-screen bg-[#0f0a0a]">
      <SynapseCodeScene />
    </main>
  );
}
