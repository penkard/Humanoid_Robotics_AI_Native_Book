import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';

const parts = [
  {
    title: 'Part 1: Introduction to Physical AI',
    path: '/docs/Part-1-introduction/overview',
    description: 'The era of Embodied Intelligence — AI systems that perceive, reason, and act in the physical world.',
  },
  {
    title: 'Part 2: Basics of Humanoid Robotics',
    path: '/docs/Part-2-humanoid-robotics/ros2-basics',
    description: 'Foundations of humanoid robotics: ROS 2 basics, URDF modeling, kinematics, and locomotion.',
  },
  {
    title: 'Part 3: ROS 2 Fundamentals',
    path: '/docs/Part-3-ros2/nodes-topics',
    description: 'Deep dive into nodes, topics, services, actions, and URDF humanoid modeling.',
  },
  {
    title: 'Part 4: Digital Twin Simulation',
    path: '/docs/Part-4-digital-twin/gazebo',
    description: 'Physics simulation with Gazebo, photorealistic rendering with NVIDIA Isaac Sim.',
  },
  {
    title: 'Part 5: Vision-Language-Action Systems',
    path: '/docs/Part-5-vla/vla-overview',
    description: 'VLA pipelines that translate natural language commands into physical robot actions.',
  },
  {
    title: 'Part 6: Capstone',
    path: '/docs/Part-6-capstone/capstone-project',
    description: 'Integrate everything: perception, planning, navigation, and manipulation.',
  },
];

export default function Home(): React.ReactElement {
  return (
    <Layout title="Home" description="Humanoid Robotics: Physical AI">
      <main style={{maxWidth: 800, margin: '0 auto', padding: '2rem 1rem'}}>
        <div style={{textAlign: 'center', marginBottom: '3rem'}}>
          <h1>Humanoid Robotics: Physical AI</h1>
          <p style={{fontSize: '1.2rem', color: 'var(--ifm-color-emphasis-700)'}}>
            Build humanoid robots that perceive, reason, and act in the real world.
          </p>
        </div>

        <h2>Table of Contents</h2>
        <div style={{display: 'flex', flexDirection: 'column', gap: '1rem'}}>
          {parts.map((part, idx) => (
            <Link
              key={idx}
              to={part.path}
              style={{
                display: 'block',
                padding: '1rem 1.5rem',
                borderRadius: '8px',
                border: '1px solid var(--ifm-color-emphasis-300)',
                textDecoration: 'none',
                color: 'inherit',
              }}
            >
              <strong>{part.title}</strong>
              <p style={{margin: '0.5rem 0 0', fontSize: '0.9rem', color: 'var(--ifm-color-emphasis-600)'}}>
                {part.description}
              </p>
            </Link>
          ))}
        </div>
      </main>
    </Layout>
  );
}
