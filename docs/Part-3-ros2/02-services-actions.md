---
sidebar_position: 2
title: "Services and Actions"
---

# Services and Actions

## Beyond Publish-Subscribe

Topics handle continuous data streams well — sensor data, state updates, command velocities. But some interactions need a request-response pattern:

- "Compute a navigation path from A to B" (takes time, returns a result)
- "Calibrate the IMU" (one-shot operation)
- "Pick up the object at position (x, y, z)" (long-running with progress feedback)

ROS 2 provides two mechanisms for this: **Services** and **Actions**.

## Services

A **service** is a synchronous request-response call. The client sends a request and blocks until the server responds.

```python
from example_interfaces.srv import AddTwoInts
import rclpy
from rclpy.node import Node

class MinimalService(Node):
    def __init__(self):
        super().__init__('minimal_service')
        self.srv = self.create_service(
            AddTwoInts,
            'add_two_ints',
            self.add_callback
        )

    def add_callback(self, request, response):
        response.sum = request.a + request.b
        self.get_logger().info(f'{request.a} + {request.b} = {response.sum}')
        return response
```

Use services when the operation is fast and the caller can wait.

## Actions

An **action** is an asynchronous goal-based interface. The client sends a goal, receives periodic feedback, and eventually gets a result. Actions can be cancelled mid-execution.

```
Client sends goal → Server accepts → Server sends feedback (0%... 50%... 90%) → Server sends result
```

Actions are the right choice for long-running robot tasks: navigation, manipulation, and perception pipelines.

## When to Use What

| Pattern | Use Case | Blocking? | Feedback? |
|---------|----------|-----------|-----------|
| Topic | Continuous data streams | No | N/A |
| Service | Fast request-response | Yes | No |
| Action | Long-running tasks | No | Yes |

## Next Steps

With nodes, topics, services, and actions, you have the full ROS 2 communication toolkit. Next, we model the robot itself using **URDF** — the Unified Robot Description Format.
