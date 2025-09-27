#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import yaml
import os
import math
from ament_index_python.packages import get_package_share_directory

class WaypointExecutorSingle(Node):
    def __init__(self):
        super().__init__('waypoint_executor_single')
        
        # Action client for navigate_to_pose (single goal navigation)
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        
        # Load waypoints from YAML
        self.waypoints = self.load_waypoints()
        self.current_waypoint_index = 0
        
        # Timer to start execution after a delay
        self.timer = self.create_timer(3.0, self.start_navigation)
        
    def load_waypoints(self):
        try:
            # Get the package directory
            package_dir = get_package_share_directory('turtlebot3_custom_bt')
            waypoints_file = os.path.join(package_dir, 'config', 'waypoints.yaml')
            
            self.get_logger().info(f'Loading waypoints from: {waypoints_file}')
            
            with open(waypoints_file, 'r') as file:
                data = yaml.safe_load(file)
                waypoints = data.get('waypoints', [])
                self.get_logger().info(f'Loaded {len(waypoints)} waypoints')
                return waypoints
                
        except Exception as e:
            self.get_logger().error(f'Failed to load waypoints: {e}')
            # Return some default waypoints for testing
            return [
                {'x': 1.0, 'y': 0.0, 'theta': 0.0},
                {'x': 1.0, 'y': 1.0, 'theta': 1.57},
                {'x': 0.0, 'y': 1.0, 'theta': 3.14},
                {'x': 0.0, 'y': 0.0, 'theta': 0.0}
            ]
    
    def start_navigation(self):
        # Cancel the timer
        self.timer.cancel()
        
        # Wait for action server
        self.get_logger().info('Waiting for navigate_to_pose action server...')
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('navigate_to_pose action server not available!')
            return
        
        # Start navigating to first waypoint
        self.navigate_to_next_waypoint()
    
    def create_pose_stamped(self, waypoint):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        
        pose.pose.position.x = float(waypoint['x'])
        pose.pose.position.y = float(waypoint['y'])
        pose.pose.position.z = 0.0
        
        # Convert theta to quaternion
        theta = waypoint.get('theta', waypoint.get('yaw', 0.0))
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = math.sin(theta / 2.0)
        pose.pose.orientation.w = math.cos(theta / 2.0)
        
        return pose
    
    def navigate_to_next_waypoint(self):
        if self.current_waypoint_index >= len(self.waypoints):
            self.get_logger().info('✅ All waypoints completed successfully!')
            return
        
        waypoint = self.waypoints[self.current_waypoint_index]
        pose = self.create_pose_stamped(waypoint)
        
        # Create goal message for single pose navigation
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = pose
        
        self.get_logger().info(f'📍 Navigating to waypoint {self.current_waypoint_index + 1}/{len(self.waypoints)}: x={waypoint["x"]}, y={waypoint["y"]}, theta={waypoint.get("theta", waypoint.get("yaw", 0.0))}')
        
        # Send goal
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, 
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)
    
    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error(f'Goal rejected for waypoint {self.current_waypoint_index + 1}!')
            return
        
        self.get_logger().info(f'Goal accepted for waypoint {self.current_waypoint_index + 1}')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)
    
    def get_result_callback(self, future):
        result = future.result().result
        
        if result:
            self.get_logger().info(f'✅ Reached waypoint {self.current_waypoint_index + 1}')
            self.current_waypoint_index += 1
            
            # Navigate to next waypoint after a very short delay
            self.timer = self.create_timer(0.5, self.navigate_to_next_waypoint_delayed)  # 0.5 second pause
        else:
            self.get_logger().warn(f'⚠️ Failed to reach waypoint {self.current_waypoint_index + 1}')
            self.current_waypoint_index += 1
            
            # Try next waypoint anyway
            self.timer = self.create_timer(1.0, self.navigate_to_next_waypoint_delayed)  # 1 second pause after failure
    
    def navigate_to_next_waypoint_delayed(self):
        self.timer.cancel()
        self.navigate_to_next_waypoint()
    
    def feedback_callback(self, feedback_msg):
        # You can add distance remaining or other feedback here if needed
        pass

def main(args=None):
    rclpy.init(args=args)
    
    try:
        executor = WaypointExecutorSingle()
        rclpy.spin(executor)
    except KeyboardInterrupt:
        pass
    finally:
        if 'executor' in locals():
            executor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()