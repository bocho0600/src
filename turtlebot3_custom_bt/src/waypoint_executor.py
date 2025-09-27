#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateThroughPoses
from geometry_msgs.msg import PoseStamped
import yaml
import os
import math
from ament_index_python.packages import get_package_share_directory

class WaypointExecutor(Node):
    def __init__(self):
        super().__init__('waypoint_executor')
        
        # Action client for navigate_through_poses
        self._action_client = ActionClient(self, NavigateThroughPoses, 'navigate_through_poses')
        
        # Load waypoints from YAML
        self.waypoints = self.load_waypoints()
        
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
                {'x': 1.0, 'y': 0.0, 'yaw': 0.0},
                {'x': 1.0, 'y': 1.0, 'yaw': 1.57},
                {'x': 0.0, 'y': 1.0, 'yaw': 3.14},
                {'x': 0.0, 'y': 0.0, 'yaw': 0.0}
            ]
    
    def start_navigation(self):
        # Cancel the timer
        self.timer.cancel()
        
        # Wait for action server
        self.get_logger().info('Waiting for navigate_through_poses action server...')
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('navigate_through_poses action server not available!')
            return
        
        # Execute waypoints
        self.execute_waypoints()
    
    def create_pose_stamped(self, waypoint):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        
        pose.pose.position.x = float(waypoint['x'])
        pose.pose.position.y = float(waypoint['y'])
        pose.pose.position.z = 0.0
        
        # Convert theta to quaternion (using theta or yaw)
        yaw = waypoint.get('theta', waypoint.get('yaw', 0.0))
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = math.sin(yaw / 2.0)
        pose.pose.orientation.w = math.cos(yaw / 2.0)
        
        return pose
    
    def execute_waypoints(self):
        if not self.waypoints:
            self.get_logger().error('No waypoints to execute!')
            return
        
        # Convert waypoints to PoseStamped messages
        poses = [self.create_pose_stamped(wp) for wp in self.waypoints]
        
        # Create goal message
        goal_msg = NavigateThroughPoses.Goal()
        goal_msg.poses = poses
        
        self.get_logger().info(f'Sending {len(poses)} waypoints to navigate_through_poses')
        for i, wp in enumerate(self.waypoints):
            theta = wp.get('theta', wp.get('yaw', 0.0))
            self.get_logger().info(f'  Waypoint {i+1}: x={wp["x"]}, y={wp["y"]}, theta={theta}')
        
        # Send goal
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, 
            feedback_callback=self.feedback_callback
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)
    
    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by navigate_through_poses!')
            return
        
        self.get_logger().info('Goal accepted! Starting waypoint navigation...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)
    
    def get_result_callback(self, future):
        result = future.result().result
        if result:
            self.get_logger().info('✅ All waypoints completed successfully!')
        else:
            self.get_logger().warn('⚠️  Waypoint navigation completed with issues')
    
    def feedback_callback(self, feedback_msg):
        current_waypoint = feedback_msg.feedback.current_waypoint
        total_waypoints = len(self.waypoints)
        self.get_logger().info(f'📍 Progress: Navigating to waypoint {current_waypoint + 1}/{total_waypoints}')

def main(args=None):
    rclpy.init(args=args)
    
    try:
        executor = WaypointExecutor()
        rclpy.spin(executor)
    except KeyboardInterrupt:
        pass
    finally:
        if 'executor' in locals():
            executor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()