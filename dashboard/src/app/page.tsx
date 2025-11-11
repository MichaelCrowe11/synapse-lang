'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 text-white">
      <div className="container mx-auto px-6 py-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-20"
        >
          <h1 className="text-7xl font-bold mb-6 bg-gradient-to-r from-cyan-400 via-purple-400 to-teal-400 bg-clip-text text-transparent">
            Crowe Logic Ecosystem
          </h1>
          <p className="text-2xl text-gray-300 max-w-3xl mx-auto">
            Systematic methodology meets biological intelligence. Experience the future of
            intelligent systems through liquid glass morphism and cinematic immersion.
          </p>
        </motion.div>

        {/* Platform Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Crowe Code */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Link href="/crowe-code">
              <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-900/50 to-purple-900/50 p-8 border border-cyan-500/30 hover:border-cyan-400 transition-all duration-300 cursor-pointer h-full">
                {/* Circuit pattern background */}
                <div className="absolute inset-0 opacity-10 pointer-events-none"
                  style={{
                    backgroundImage: `linear-gradient(#00d9ff 1px, transparent 1px),
                                     linear-gradient(90deg, #00d9ff 1px, transparent 1px)`,
                    backgroundSize: '30px 30px'
                  }}
                />

                <div className="relative z-10">
                  <div className="text-cyan-400 text-5xl mb-4">⚡</div>
                  <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                    Crowe Code
                  </h2>
                  <p className="text-xl text-cyan-300 mb-4 font-semibold">
                    Where AI Meets Code Intelligence
                  </p>
                  <p className="text-gray-300 mb-6 leading-relaxed">
                    Neural networks forming connections, data flowing through circuits. Experience
                    obsidian glass with electric neural pathways, powered by 150+ AI agents working
                    in algorithmic harmony.
                  </p>

                  <div className="flex flex-wrap gap-2 mb-6">
                    <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 rounded-full text-sm">
                      Neural Networks
                    </span>
                    <span className="px-3 py-1 bg-purple-500/20 text-purple-300 rounded-full text-sm">
                      Obsidian Glass
                    </span>
                    <span className="px-3 py-1 bg-cyan-500/20 text-cyan-300 rounded-full text-sm">
                      Electric Blue
                    </span>
                  </div>

                  <div className="text-cyan-400 group-hover:translate-x-2 transition-transform duration-300 inline-flex items-center">
                    Experience Crowe Code →
                  </div>
                </div>
              </div>
            </Link>
          </motion.div>

          {/* Synapse-Code */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
          >
            <Link href="/synapse-code">
              <div className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-teal-900/50 to-amber-900/50 p-8 border border-teal-500/30 hover:border-teal-400 transition-all duration-300 cursor-pointer h-full">
                {/* Organic pattern background */}
                <div className="absolute inset-0 opacity-10 pointer-events-none"
                  style={{
                    backgroundImage: `radial-gradient(circle, #00ffd9 1px, transparent 1px)`,
                    backgroundSize: '40px 40px'
                  }}
                />

                <div className="relative z-10">
                  <div className="text-teal-400 text-5xl mb-4">🍄</div>
                  <h2 className="text-4xl font-bold mb-4 bg-gradient-to-r from-teal-400 to-amber-400 bg-clip-text text-transparent">
                    Synapse-Code
                  </h2>
                  <p className="text-xl text-teal-300 mb-4 font-semibold">
                    Fungal Intelligence, Evolved
                  </p>
                  <p className="text-gray-300 mb-6 leading-relaxed">
                    Mycelial networks spreading, spores releasing, fungal wisdom emerging. Experience
                    organic liquid glass with bioluminescent flow, where code grows and adapts like
                    living intelligence.
                  </p>

                  <div className="flex flex-wrap gap-2 mb-6">
                    <span className="px-3 py-1 bg-teal-500/20 text-teal-300 rounded-full text-sm">
                      Mycelial Growth
                    </span>
                    <span className="px-3 py-1 bg-amber-500/20 text-amber-300 rounded-full text-sm">
                      Organic Glass
                    </span>
                    <span className="px-3 py-1 bg-teal-500/20 text-teal-300 rounded-full text-sm">
                      Bioluminescence
                    </span>
                  </div>

                  <div className="text-teal-400 group-hover:translate-x-2 transition-transform duration-300 inline-flex items-center">
                    Experience Synapse-Code →
                  </div>
                </div>
              </div>
            </Link>
          </motion.div>
        </div>

        {/* Philosophy Section */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mt-20 text-center max-w-4xl mx-auto"
        >
          <h3 className="text-3xl font-bold mb-6 text-purple-300">Our Philosophy</h3>
          <p className="text-lg text-gray-300 leading-relaxed">
            At Crowe Logic, we believe technology should be as beautiful as it is powerful. Through
            advanced liquid glass morphism and state-of-the-art rendering techniques, we create
            experiences that don't just showcase technology—they make you feel it. Whether it's
            the electric precision of neural code intelligence or the organic wisdom of mycelial
            networks, every interaction is designed to inspire wonder.
          </p>
        </motion.div>

        {/* Technical Excellence */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mt-16 grid md:grid-cols-3 gap-6 max-w-6xl mx-auto"
        >
          <div className="text-center p-6 rounded-xl bg-white/5 backdrop-blur-sm">
            <div className="text-4xl mb-3">⚡</div>
            <h4 className="text-xl font-bold mb-2 text-cyan-300">60 FPS Performance</h4>
            <p className="text-gray-400">Research-grade CGI on web platform with adaptive quality</p>
          </div>

          <div className="text-center p-6 rounded-xl bg-white/5 backdrop-blur-sm">
            <div className="text-4xl mb-3">🎨</div>
            <h4 className="text-xl font-bold mb-2 text-purple-300">Advanced Shaders</h4>
            <p className="text-gray-400">Custom WebGL shaders for photorealistic materials</p>
          </div>

          <div className="text-center p-6 rounded-xl bg-white/5 backdrop-blur-sm">
            <div className="text-4xl mb-3">🧬</div>
            <h4 className="text-xl font-bold mb-2 text-teal-300">Biologically Inspired</h4>
            <p className="text-gray-400">L-systems and neural networks brought to life</p>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
