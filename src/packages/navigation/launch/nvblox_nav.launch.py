# SPDX-FileCopyrightText: NVIDIA CORPORATION & AFFILIATES
# SPDX-License-Identifier: Apache-2.0

import os
from isaac_ros_launch_utils.all_types import *
import isaac_ros_launch_utils as lu

from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch import LaunchDescription

from nvblox_ros_python_utils.nvblox_launch_utils import NvbloxMode, NvbloxCamera
from nvblox_ros_python_utils.nvblox_constants import NVBLOX_CONTAINER_NAME
from ament_index_python.packages import get_package_share_directory


def add_optional_nodes(context, *args, **kwargs):
    actions = []

    # Resolve launch arguments to real strings
    use_nvblox = LaunchConfiguration('use_nvblox').perform(context)
    use_vslam = LaunchConfiguration('use_vslam').perform(context)
    use_navigation = LaunchConfiguration('use_navigation').perform(context)

    # Convert to real booleans
    use_nvblox = use_nvblox.lower() == 'true'
    use_vslam = use_vslam.lower() == 'true'
    use_navigation = use_navigation.lower() == 'true'

    camera_mode = NvbloxCamera.realsense

    # Visual SLAM
    if use_vslam:
        actions.append(
            lu.include(
                'navigation',
                'launch/perception/vslam.launch.py',
                launch_arguments={
                    'container_name': NVBLOX_CONTAINER_NAME,
                    'camera': camera_mode,
                },
            ))

    # Nvblox
    if use_nvblox:
        actions.append(
            lu.include(
                'navigation',
                'launch/perception/nvblox.launch.py',
                launch_arguments={
                    'mode': 'static',
                    'camera': camera_mode,
                    'num_cameras': 1,
                    # Build the 3D map in the SLAM-corrected map frame so it lines up with the
                    # 2D map; without slam_toolbox there is no map frame, so stay in odom
                    'global_frame': 'map' if use_navigation else 'odom',
                }))


    # Navigation
    if use_navigation:
        actions.append(
            lu.include(
                'navigation',
                'launch/lidar_nav.launch.py',
                launch_arguments={
                    'nvblox_costmap': use_nvblox
                }))


    return actions


def generate_launch_description() -> LaunchDescription:

    args = lu.ArgumentContainer()
    args.add_arg('log_level', 'info', choices=['debug', 'info', 'warn'], cli=True)
    args.add_arg(
        'mode',
        default=NvbloxMode.static,
        choices=NvbloxMode.names(),
        description='The nvblox mode.',
        cli=True)

    # Boolean flags
    launch_args = [
        DeclareLaunchArgument('use_nvblox', default_value='true'),
        DeclareLaunchArgument('use_vslam', default_value='true'),
        DeclareLaunchArgument('use_navigation', default_value='true'),
    ]

    actions = launch_args + args.get_launch_actions()

    camera_mode = NvbloxCamera.realsense

    # Sensors
    actions.append(
        lu.include(
            'navigation',
            'launch/sensors/realsense.launch.py',
            launch_arguments={
                'camera_serial_numbers': '',
                'num_cameras': 1,
            }))

    # Optional nodes (nvblox / vslam)
    actions.append(OpaqueFunction(function=add_optional_nodes))

    # Visualization
    actions.append(
        lu.include(
            'navigation',
            'launch/visualization/visualization.launch.py',
            launch_arguments={
                'mode': args.mode,
                'camera': camera_mode,
                'use_foxglove_whitelist': False,
            }))

    ekf_param_file = os.path.join(get_package_share_directory('navigation'),
                                   'config', 'filtering', 'ekf.yaml')

    actions.append(Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_param_file]
        ))

    # Component container
    actions.append(
        lu.component_container(
            NVBLOX_CONTAINER_NAME,
            log_level=args.log_level))

    # Republish image
    actions.append(Node(
        package='topic_tools',
        executable='relay',
        name='image_relay',
        arguments=[
            '/camera0/color/image_raw',
            '/image_rect'
        ],
        output='screen'
    ))

    # Republish camera info
    actions.append(Node(
        package='topic_tools',
        executable='relay',
        name='camera_info_relay',
        arguments=[
            '/camera0/color/camera_info',
            '/camera_info_rect'
        ],
        output='screen'
    ))

    return LaunchDescription(actions)
