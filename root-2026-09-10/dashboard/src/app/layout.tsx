import type { Metadata } from 'next';
import { Providers } from './providers';
import './globals.css';

export const metadata: Metadata = {
  title: 'Crowe Logic Ecosystem - Cinematic Code Intelligence',
  description: 'Experience the future of intelligent systems through Crowe Code (neural AI) and Synapse-Code (fungal networks). Advanced liquid glass morphism meets cutting-edge code generation.',
  keywords: ['AI', 'code generation', 'neural networks', 'mycelial intelligence', 'quantum computing', 'WebGL', 'Three.js'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}