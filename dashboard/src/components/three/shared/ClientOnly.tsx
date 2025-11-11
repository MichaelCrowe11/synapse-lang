'use client';

import dynamic from 'next/dynamic';
import { ComponentType } from 'react';

export function createClientComponent<P extends object>(
  Component: ComponentType<P>
) {
  return dynamic(() => Promise.resolve(Component), {
    ssr: false,
    loading: () => (
      <div className="w-full h-screen flex items-center justify-center bg-black">
        <div className="text-white text-xl">Loading...</div>
      </div>
    ),
  });
}
