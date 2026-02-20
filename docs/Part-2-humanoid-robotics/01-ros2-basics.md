---
sidebar_position: 1
title: "ROS 2 Basics"
---

# ROS 2 — The Robotic Nervous System

If the AI is the brain and the motors are the muscles, **ROS 2 (Robot Operating System 2)** is the nervous system. It is the industry-standard middleware that allows different parts of a robot to communicate with low latency.

## Why ROS 2?

ROS 2 serves as the communication backbone for modern robots, enabling various components to work together effectively. Its core communication mechanisms include **nodes**, **topics**, **services**, and **actions**.

## ROS 2 Core Concepts and Architecture

ROS 2 operates on a **Graph Architecture**.

### Nodes

A **Node** is a single executable process that performs a specific task.
- One node controls the camera driver
- Another node processes the image
- A third node controls the wheels

### Topics

Nodes communicate by publishing messages to **Topics**.
- **Publisher:** A node that sends data (e.g., Camera Node sends images)
- **Subscriber:** A node that receives data (e.g., Object Detection Node receives images)

Think of a Topic as a broadcast channel. The Publisher sends data, and all Subscribers receive it automatically.

### Architecture Components

- **Middleware (DDS):** ROS 2 uses **Data Distribution Service (DDS)** as its core middleware, providing quality-of-service settings and low-latency, real-time communication.
- **Launch Files:** Used to start and configure multiple nodes and components simultaneously.
- **Parameters:** Used to configure nodes at runtime (e.g., setting the exposure of a camera node).

## Writing ROS 2 Nodes in Python (rclpy)

We use the `rclpy` library to bridge Python AI agents with robotic hardware.

### A Simple Publisher Node

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello, Physical World!'
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)

def main(args=None):
    rclpy.init(args=args)
    minimal_publisher = MinimalPublisher()
    rclpy.spin(minimal_publisher)
    minimal_publisher.destroy_node()
    rclpy.shutdown()
```

### Development Steps

1. **Creating a package:** The initial step for organizing your ROS 2 code
2. **Writing nodes using `rclpy`:** Implementing the specific functionality of your robot component
3. **Publishing sensor data:** Sending out information like wheel encoders or IMU data
4. **Subscribing to camera feeds:** Receiving input from sensors for processing
