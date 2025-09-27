#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation time'
    )
    
    autostart_arg = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )
    
    rviz_arg = DeclareLaunchArgument(
        'rviz',
        default_value='true',
        description='Launch RViz for visualization'
    )

    # Get package share directories
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    custom_bt_dir = get_package_share_directory('turtlebot3_custom_bt')
    rviz_config = os.path.join(get_package_share_directory('turtlebot3_navigation_stack'), 'rviz', 'rviz.rviz')
    custom_nav2_params = os.path.join(custom_bt_dir, 'config', 'nav2_params.yaml')

    # TurtleBot3 Gazebo world launch
    turtlebot3_world_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(turtlebot3_gazebo_dir, 'launch', 'turtlebot3_world.launch.py')
        ])
    )

    # SLAM Toolbox launch (delayed to allow Gazebo to fully start)
    slam_toolbox_launch = TimerAction(
        period=5.0,  # Wait 5 seconds before starting SLAM
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    os.path.join(slam_toolbox_dir, 'launch', 'online_async_launch.py')
                ]),
                launch_arguments={
                    'use_sim_time': LaunchConfiguration('use_sim_time')
                }.items()
            )
        ]
    )

    # Nav2 launch (delayed to allow SLAM to start)
    nav2_launch = TimerAction(
        period=10.0,  # Wait 10 seconds before starting Nav2
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')
                ]),
                launch_arguments={
                    'use_sim_time': LaunchConfiguration('use_sim_time'),
                    'autostart': LaunchConfiguration('autostart'),
                    'params_file': custom_nav2_params
                }.items()
            )
        ]
    )

    # RViz launch (delayed to allow everything else to start)
    rviz_launch = TimerAction(
        period=12.0,  # Wait 12 seconds before starting RViz
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                arguments=['-d', rviz_config],
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                condition=IfCondition(LaunchConfiguration('rviz'))
            )
        ]
    )

        # Set initial pose (delayed to allow SLAM to be ready)
    initial_pose_publisher = TimerAction(
        period=15.0,  # Wait 15 seconds for everything to be ready
        actions=[
            Node(
                package='turtlebot3_custom_bt',
                executable='initial_pose_publisher',
                name='initial_pose_publisher',
                parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        use_sim_time_arg,
        autostart_arg,
        rviz_arg,
        turtlebot3_world_launch,
        slam_toolbox_launch,
        nav2_launch,
        rviz_launch,
        initial_pose_publisher
    ])