---
sidebar_position: 1
title: "ROS 2 Nodes and Topics"
---

# ROS 2 Nodes and Topics

## Why ROS 2?

A humanoid robot is a distributed system. Its cameras, actuators, planners, and controllers are separate processes that must communicate in real time. ROS 2 (Robot Operating System 2) provides the middleware that connects them.

Think of ROS 2 as the nervous system of the robot: nodes are neurons, and topics are the axons that carry signals between them.

## Nodes

A **node** is a single-purpose process in the ROS 2 computation graph. Each node handles one responsibility:

```python
import rclpy
from rclpy.node import Node

class MinimalPublisher(Node):
    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(String, 'topic', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        msg = String()
        msg.data = 'Hello from the robot nervous system'
        self.publisher_.publish(msg)
```

Key properties of nodes:
- **Single responsibility**: one node, one job
- **Discoverable**: nodes announce themselves on the ROS 2 network
- **Lifecycle-managed**: nodes can be started, configured, activated, and shut down programmatically

## Topics

**Topics** are named buses for asynchronous message passing. A publisher sends messages to a topic; any number of subscribers can listen.

```bash
# List all active topics
ros2 topic list

# Echo messages on a topic
ros2 topic echo /camera/image_raw
```

The publish-subscribe pattern decouples producers from consumers. The camera node does not need to know who is reading its images.

## Putting It Together

A minimal humanoid perception pipeline:

```
[Camera Node] --/image_raw--> [Perception Node] --/detected_objects--> [Planner Node]
```

Each arrow is a topic. Each box is a node. The system scales by adding nodes without modifying existing ones.

## Next Steps

In the next section, we cover **Services and Actions** — synchronous request-response patterns for when publish-subscribe is not enough.
