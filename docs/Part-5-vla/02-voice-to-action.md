---
sidebar_position: 2
title: "Voice-to-Action Pipeline"
---

# Voice-to-Action Pipeline

## End-to-End Architecture

The Voice-to-Action pipeline integrates speech recognition, LLM-based planning, perception, and robot control into a single autonomous workflow.

```
Voice Command → Speech-to-Text → LLM Task Planner → Motion Primitives → ROS 2 Actions → Robot Execution
```

## Speech-to-Text Integration

```python
import whisper

model = whisper.load_model("base")

def transcribe_command(audio_path: str) -> str:
    """Convert spoken command to text using Whisper."""
    result = model.transcribe(audio_path)
    return result["text"]
```

Whisper handles multiple languages and noisy environments, making it suitable for real-world robot deployments where background noise is common.

## LLM-Based Task Planning

The LLM receives the transcribed command along with the robot's current state and available capabilities:

```python
PLANNER_PROMPT = """
You are a robot task planner. Given a natural language command,
break it down into a sequence of executable actions.

Available actions:
- navigate_to(location)
- pick_up(object)
- place_at(location)
- open(object)
- close(object)
- wait(seconds)

Current state: {robot_state}
Command: {command}

Return a JSON array of actions.
"""
```

## Action Execution via ROS 2

Each planned action maps to a ROS 2 Action Server:

```python
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose

class NavigationClient(Node):
    def __init__(self):
        super().__init__('navigation_client')
        self._action_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose'
        )

    def send_goal(self, x, y, theta):
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        self._action_client.send_goal_async(goal_msg)
```

## Perception Pipeline

The perception system runs continuously, updating the robot's world model:

1. **Object Detection** (YOLO/DINOv2) identifies objects in the scene
2. **Depth Estimation** from RGB-D cameras provides spatial coordinates
3. **Scene Graph** maintains a structured representation of detected objects and their relationships
4. **Grasp Planning** determines optimal grasp poses for target objects

## Error Recovery

Real-world execution rarely follows the plan perfectly. The system must handle:

- **Failed grasps:** Re-attempt with adjusted grasp pose
- **Blocked paths:** Re-plan navigation around obstacles
- **Unrecognized objects:** Ask for human clarification
- **Timeout:** Abort current action and report failure
