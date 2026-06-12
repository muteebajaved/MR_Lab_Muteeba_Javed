# camera_follower

A ROS 2 package that enables a robot to visually detect and follow colored objects using a camera. The package contains three progressive nodes, with the **CLR Follower** (`clr_follower`) as the final, most capable node.

---

## Package Overview

| Node | Script | Entry Point | Description |
|------|--------|-------------|-------------|
| Camera Tracker | `tracking.py` | `tracking` | Basic red-object tracker (rotate to center only) |
| Camera Follower | `camera_follower.py` | `camera_follower` | State-machine follower for red objects (Search → Align → Approach → Stop) |
| **CLR Follower** | `clr_follower.py` | `clr_follower` | **Final node** — multi-color priority follower with 360° search and goal detection |

---

## Dependencies

- ROS 2 (Humble or later)
- `rclpy`
- `sensor_msgs` (`Image`)
- `geometry_msgs` (`Twist`)
- `cv_bridge`
- `OpenCV` (`cv2`)
- `numpy`

---

## Building the Package

```bash
cd ~/ros2_ws_alishba
colcon build --packages-select camera_follower
source install/setup.bash
```

---

## Nodes

### 1. Camera Tracker (`tracking`)

A simple proportional controller that detects **red** objects and rotates to keep them centered.

**Run:**
```bash
ros2 run camera_follower tracking
```

**Topics:**
| Direction | Topic | Type |
|-----------|-------|------|
| Subscribe | `/camera/image_raw` | `sensor_msgs/Image` |
| Publish   | `/cmd_vel`           | `geometry_msgs/Twist` |

**Behavior:**
- Spins in place to search for a red object
- Rotates to center the detected object using proportional control
- Does **not** move forward

---

### 2. Camera Follower (`camera_follower`)

A state-machine-based node that detects **red** objects and physically approaches them.

**Run:**
```bash
ros2 run camera_follower camera_follower
```

**Topics:**
| Direction | Topic | Type |
|-----------|-------|------|
| Subscribe | `/camera/image_raw` | `sensor_msgs/Image` |
| Publish   | `/cmd_vel`           | `geometry_msgs/Twist` |

**States:**

```
SEARCH → ALIGN → APPROACH → STOP
```

| State | Behavior |
|-------|----------|
| `SEARCH` | Slowly rotates to find a red object |
| `ALIGN` | Centers the object horizontally (angular-only correction) |
| `APPROACH` | Moves forward while maintaining alignment |
| `STOP` | Halts when the object fills a threshold area |

**Key Parameters:**
| Parameter | Value | Description |
|-----------|-------|-------------|
| `kp_ang` | `0.0012` | Angular proportional gain |
| `align_thresh` | `12 px` | Error tolerance for alignment |
| `linear_speed` | `0.18 m/s` | Forward approach speed |
| `stop_area` | `1,600,000 px²` | Contour area at which to stop |

---

### 3. CLR Follower (`clr_follower`)  Final Node

The most advanced node in the package. Detects and follows **multiple colored objects** with a strict priority order, features a proportional approach controller based on fill percentage, and performs an automated **360° rotation search** when the target is lost.

**Run:**
```bash
ros2 run camera_follower clr_follower
```

**Topics:**
| Direction | Topic | Type |
|-----------|-------|------|
| Subscribe | `/camera/image_raw` | `sensor_msgs/Image` |
| Publish   | `/cmd_vel`           | `geometry_msgs/Twist` |

#### Color Priority

Detection is evaluated in strict priority order. The **first** color found takes control:

```
🔴 RED  >  🔵 BLUE  >  🟢 GREEN
```

| Color | HSV Range(s) |
|-------|-------------|
| RED | `[0,150,70]→[10,255,255]` and `[160,150,70]→[180,255,255]` |
| BLUE | `[100,100,50]→[130,255,255]` |
| GREEN | `[40,50,50]→[80,255,255]` |

#### Behavior State Machine

```
Initial Search
     │
     ▼
Object Detected? ──No──► Rotate to search (360°)
     │                         │
     │                    Exhausted?──Yes──► STOP (no object found)
     ▼
  ALIGNING
  (centering object horizontally)
     │
     ▼
  APPROACHING
  (moving forward toward object)
     │
     ▼
Fill % ≥ 65%?──Yes──►  GOAL ACHIEVED (stop + green overlay)
```

#### Key Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `kp` | `0.0005` | Angular proportional gain |
| `center_threshold` | `3 px` | Pixel error tolerance for centering |
| `min_contour_area` | `500 px²` | Minimum detection area |
| `forward_speed` | `0.15 m/s` | Approach speed |
| `search_speed` | `0.3 rad/s` | Rotation speed during search |
| `stop_percent` | `65.0 %` | Fill percentage to trigger goal achieved |

#### 360° Search Logic

If an object was previously detected and is then lost:
1. A timer starts and the robot rotates at `search_speed`.
2. If the object is re-acquired, the timer resets and tracking resumes.
3. If a **full rotation** completes (≈ `2π / search_speed` seconds) without re-detection, the robot **stops** and reports `NO OBJECT FOUND`.

#### Visual Overlays (OpenCV Windows)

Two windows are displayed during operation:

| Window | Contents |
|--------|----------|
| `Camera View — CLR Follower` | Live camera feed with contour, centroid, status label, error, and fill% |
| `Color Mask — CLR Follower` | Binary mask of the currently tracked color |

**Goal Achieved overlay:** When the robot reaches the target (fill ≥ 65%), the camera view shows a green-tinted full-frame overlay with the text **"POINT ACHIEVED"**.

---

## Quick Start

```bash
# Terminal 1 — Launch your robot / simulation
# (e.g., TurtleBot3 Gazebo or a real robot with a USB camera)

# Terminal 2 — Run the CLR Follower (final node)
cd ~/ros2_ws_alishba
source install/setup.bash
ros2 run camera_follower clr_follower
```

---

## File Structure

```
camera_follower/
├── camera_follower/
│   ├── __init__.py
│   ├── tracking.py          # Node 1: Basic red tracker
│   ├── camera_follower.py   # Node 2: State-machine follower
│   └── clr_follower.py      # Node 3: Final multi-color CLR follower 
├── resource/
│   └── camera_follower
├── package.xml
├── setup.py
└── README.md
```

---

## Author

**MuteebaJaved** — `muteebajaved5@gmail.com`
