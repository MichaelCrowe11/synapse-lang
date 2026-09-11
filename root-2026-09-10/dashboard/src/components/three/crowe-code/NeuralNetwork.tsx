'use client';

import { useRef, useMemo, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface NeuralNode {
  id: number;
  position: THREE.Vector3;
  activation: number;
  connections: number[];
}

interface NeuralNetworkProps {
  nodeCount?: number;
  layers?: number;
  spread?: number;
  activeColor?: THREE.Color;
  inactiveColor?: THREE.Color;
}

export function NeuralNetwork({
  nodeCount = 100,
  layers = 5,
  spread = 10,
  activeColor = new THREE.Color('#00d9ff'),
  inactiveColor = new THREE.Color('#6b00ff'),
}: NeuralNetworkProps) {
  const nodesRef = useRef<THREE.Points>(null);
  const connectionsRef = useRef<THREE.LineSegments>(null);
  const [nodes, setNodes] = useState<NeuralNode[]>([]);

  // Generate neural network structure
  const networkData = useMemo(() => {
    const nodesPerLayer = Math.ceil(nodeCount / layers);
    const generatedNodes: NeuralNode[] = [];

    // Create nodes in layers
    for (let layer = 0; layer < layers; layer++) {
      const layerNodes = layer === 0 || layer === layers - 1 ? nodesPerLayer * 0.5 : nodesPerLayer;

      for (let i = 0; i < layerNodes; i++) {
        const angle = (i / layerNodes) * Math.PI * 2;
        const radius = spread * (0.5 + Math.random() * 0.5);
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius;
        const y = (layer - layers / 2) * (spread / layers) + (Math.random() - 0.5) * 2;

        generatedNodes.push({
          id: generatedNodes.length,
          position: new THREE.Vector3(x, y, z),
          activation: Math.random(),
          connections: [],
        });
      }
    }

    // Create connections between layers
    const nodesPerLayerArray: NeuralNode[][] = [];
    let currentIndex = 0;

    for (let layer = 0; layer < layers; layer++) {
      const layerNodes = layer === 0 || layer === layers - 1
        ? Math.ceil(nodesPerLayer * 0.5)
        : nodesPerLayer;
      nodesPerLayerArray.push(generatedNodes.slice(currentIndex, currentIndex + layerNodes));
      currentIndex += layerNodes;
    }

    // Connect nodes to next layer (forward connections)
    for (let layer = 0; layer < layers - 1; layer++) {
      const currentLayer = nodesPerLayerArray[layer];
      const nextLayer = nodesPerLayerArray[layer + 1];

      currentLayer.forEach(node => {
        // Each node connects to 2-4 nodes in next layer
        const connectionCount = 2 + Math.floor(Math.random() * 3);
        const connectedIndices = new Set<number>();

        while (connectedIndices.size < Math.min(connectionCount, nextLayer.length)) {
          const targetIndex = Math.floor(Math.random() * nextLayer.length);
          connectedIndices.add(nextLayer[targetIndex].id);
        }

        node.connections = Array.from(connectedIndices);
      });
    }

    return generatedNodes;
  }, [nodeCount, layers, spread]);

  useEffect(() => {
    setNodes(networkData);
  }, [networkData]);

  // Create geometries for nodes and connections
  const { nodeGeometry, connectionGeometry } = useMemo(() => {
    // Node geometry
    const nodePositions = new Float32Array(nodes.length * 3);
    const nodeColors = new Float32Array(nodes.length * 3);
    const nodeSizes = new Float32Array(nodes.length);

    nodes.forEach((node, i) => {
      nodePositions[i * 3] = node.position.x;
      nodePositions[i * 3 + 1] = node.position.y;
      nodePositions[i * 3 + 2] = node.position.z;

      const color = inactiveColor.clone().lerp(activeColor, node.activation);
      nodeColors[i * 3] = color.r;
      nodeColors[i * 3 + 1] = color.g;
      nodeColors[i * 3 + 2] = color.b;

      nodeSizes[i] = 0.1 + node.activation * 0.2;
    });

    const nodeGeo = new THREE.BufferGeometry();
    nodeGeo.setAttribute('position', new THREE.BufferAttribute(nodePositions, 3));
    nodeGeo.setAttribute('color', new THREE.BufferAttribute(nodeColors, 3));
    nodeGeo.setAttribute('size', new THREE.BufferAttribute(nodeSizes, 1));

    // Connection geometry
    const connectionLines: number[] = [];
    const connectionColors: number[] = [];

    nodes.forEach(node => {
      node.connections.forEach(targetId => {
        const target = nodes.find(n => n.id === targetId);
        if (target) {
          // Start point
          connectionLines.push(node.position.x, node.position.y, node.position.z);
          // End point
          connectionLines.push(target.position.x, target.position.y, target.position.z);

          // Color based on average activation
          const avgActivation = (node.activation + target.activation) / 2;
          const color = inactiveColor.clone().lerp(activeColor, avgActivation);

          // Add color for both vertices
          connectionColors.push(color.r, color.g, color.b);
          connectionColors.push(color.r, color.g, color.b);
        }
      });
    });

    const connectionGeo = new THREE.BufferGeometry();
    connectionGeo.setAttribute('position', new THREE.Float32BufferAttribute(connectionLines, 3));
    connectionGeo.setAttribute('color', new THREE.Float32BufferAttribute(connectionColors, 3));

    return { nodeGeometry: nodeGeo, connectionGeometry: connectionGeo };
  }, [nodes, activeColor, inactiveColor]);

  // Animate network activity
  useFrame((state) => {
    const time = state.clock.elapsedTime;

    // Update node activations (propagate signals)
    setNodes(prevNodes =>
      prevNodes.map(node => ({
        ...node,
        activation: Math.max(0, Math.min(1,
          0.3 + Math.sin(time * 2 + node.id * 0.1) * 0.3 + Math.random() * 0.1
        ))
      }))
    );

    // Rotate entire network slowly
    if (nodesRef.current) {
      nodesRef.current.rotation.y = time * 0.1;
    }
    if (connectionsRef.current) {
      connectionsRef.current.rotation.y = time * 0.1;
    }
  });

  return (
    <group>
      {/* Connections (rendered behind nodes) */}
      <lineSegments ref={connectionsRef} geometry={connectionGeometry}>
        <lineBasicMaterial
          vertexColors
          transparent
          opacity={0.4}
          blending={THREE.AdditiveBlending}
        />
      </lineSegments>

      {/* Nodes */}
      <points ref={nodesRef} geometry={nodeGeometry}>
        <pointsMaterial
          size={0.2}
          vertexColors
          transparent
          opacity={0.9}
          sizeAttenuation
          blending={THREE.AdditiveBlending}
        />
      </points>
    </group>
  );
}
