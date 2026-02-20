---
sidebar_position: 3
title: "URDF Humanoid Modeling"
---

# URDF Humanoid Modeling

## What Is URDF?

The **Unified Robot Description Format** (URDF) is an XML specification that defines a robot's physical structure: its links (rigid bodies), joints (connections between links), and their geometric and inertial properties.

Every humanoid robot in ROS 2 starts as a URDF file. The simulator reads it. The planner reads it. The controller reads it. URDF is the shared contract between all subsystems.

## Anatomy of a URDF

```xml
<?xml version="1.0"?>
<robot name="simple_humanoid">
  <!-- Base link (torso) -->
  <link name="torso">
    <visual>
      <geometry>
        <box size="0.3 0.2 0.5"/>
      </geometry>
    </visual>
    <inertial>
      <mass value="10.0"/>
      <inertia ixx="0.1" iyy="0.1" izz="0.1"
               ixy="0" ixz="0" iyz="0"/>
    </inertial>
  </link>

  <!-- Right upper arm -->
  <link name="right_upper_arm">
    <visual>
      <geometry>
        <cylinder radius="0.04" length="0.3"/>
      </geometry>
    </visual>
  </link>

  <!-- Shoulder joint -->
  <joint name="right_shoulder" type="revolute">
    <parent link="torso"/>
    <child link="right_upper_arm"/>
    <origin xyz="0.15 0 0.2" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.57" upper="1.57" effort="10" velocity="1.0"/>
  </joint>
</robot>
```

Key elements:
- **Links**: rigid bodies with visual geometry, collision geometry, and inertial properties
- **Joints**: connections between links with type (revolute, prismatic, fixed), axis, and limits
- **Origin**: spatial relationship between parent and child links

## Visualizing the Robot

```bash
# Install URDF visualization tools
sudo apt install ros-humble-urdf-tutorial

# Launch the robot state publisher and RViz
ros2 launch urdf_tutorial display.launch.py model:=simple_humanoid.urdf
```

RViz renders the URDF as an interactive 3D model. You can move joint sliders to see how the humanoid articulates.

## From URDF to Simulation

The URDF defines what the robot looks like and how it moves. In the next module, we load this URDF into **Gazebo** and **Isaac Sim** to give it a physics engine, sensors, and a world to interact with.
