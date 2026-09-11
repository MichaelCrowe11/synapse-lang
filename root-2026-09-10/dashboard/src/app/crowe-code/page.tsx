'use client';

import dynamic from 'next/dynamic';

const CroweCodeScene = dynamic(
  () => import('./CroweCodeScene').then(mod => ({ default: mod.CroweCodeScene })),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-screen flex items-center justify-center bg-[#0a0a0f]">
        <div className="text-cyan-400 text-2xl animate-pulse">Loading Crowe Code...</div>
      </div>
    ),
  }
);

export default function CroweCodePage() {
  return (
    <main className="relative w-full h-screen bg-[#0a0a0f]">
      <CroweCodeScene />
    </main>
  );
}
