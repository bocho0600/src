# TurtleBot3 Navigation Stack

This package provides a combined launch file for running TurtleBot3 simulation with SLAM and navigation in Gazebo.

## Description

This launch file combines three separate launch commands into one:
1. `turtlebot3_gazebo turtlebot3_world.launch.py` - Starts TurtleBot3 in Gazebo world
2. `slam_toolbox online_async_launch.py` - Starts SLAM mapping
3. `nav2_bringup navigation_launch.py` - Starts Nav2 navigation stack

## Prerequisites

Make sure you have the following packages installed:
- `turtlebot3_gazebo`
- `slam_toolbox`
- `nav2_bringup`
- `turtlebot3_description`

Also ensure that your TurtleBot3 model is set:
```bash
export TURTLEBOT3_MODEL=waffle_pi
```

## Usage

1. Build the package:
```bash
cd ~/ros2_ws
colcon build --packages-select turtlebot3_navigation_stack
source install/setup.bash
```

2. Launch the complete navigation stack:
```bash
ros2 launch turtlebot3_navigation_stack turtlebot3_nav_stack.launch.py
```

3. Optional parameters:
```bash
ros2 launch turtlebot3_navigation_stack turtlebot3_nav_stack.launch.py use_sim_time:=true autostart:=false
```

## Features

- **Sequential startup**: The launch file uses timers to ensure proper startup sequence
- **Configurable parameters**: `use_sim_time` and `autostart` can be customized
- **Error handling**: Delays between launches prevent startup conflicts

## What happens when you run it:

1. **T=0s**: Gazebo starts with TurtleBot3 world
2. **T=5s**: SLAM Toolbox starts mapping
3. **T=10s**: Nav2 navigation stack starts

After everything is running, you can:
- Use RViz to visualize the map being built
- Set navigation goals using the "2D Goal Pose" tool in RViz
- Monitor the robot's progress through the navigation stack