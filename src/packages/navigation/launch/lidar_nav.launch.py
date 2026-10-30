from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

import os
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration, PythonExpression

def generate_launch_description():

    use_nvblox = LaunchConfiguration('use_nvblox')

    slam_toobox = Node(
            package='slam_toolbox',
            # executable='sync_slam_toolbox_node',   # or 'async_slam_toolbox_node'
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            # "Reset 2D map" in the feature manager ends this process to start over with an empty
            # map (slam_toolbox in Humble has no reset service); the respawn brings it back
            respawn=True,
            respawn_delay=1.0,
            parameters=[{
                # Frames
                'use_sim_time': False,
                'odom_frame': 'odom',
                'map_frame': 'map',
                'base_frame': 'base_footprint',
                'scan_topic': '/scan',

                'maximum_angular_velocity': 0.1,
                'minimum_travel_distance': 0.01,
                # 'minimum_travel_heading': 0.35,

                # Map
                'resolution': 0.03,
                'map_update_interval': 0.1,
                'mode': 'mapping',

                # Laser limits
                'min_laser_range': 0.2,
                'max_laser_range': 12.0,

                # TF robustness
                'tf_buffer_duration': 10.0,
                'transform_timeout': 0.5,

                # Odometry usage
                'use_odometry': True,
                # Penalize scan matches that deviate from odometry (score * 1 - 0.2 * d^2 / variance):
                # with the defaults (0.5, 1.0) a 10 cm offset cost only 0.4 % and the pose jittered
                # 5-15 cm back and forth. Now 10 cm cost ~7 %, 5 deg ~1.5 %.
                'distance_variance_penalty': 0.03,
                'angle_variance_penalty': 0.1,

                # Scan buffering (helps recovery)
                'scan_buffer_size': 80,
                'scan_buffer_maximum_scan_distance': 12.0,

                # Loop closure & matching
                'use_scan_matching': True,
                'use_scan_barycenter': True,
                'do_loop_closing': True,

                'ceres_scan_matcher': {
                    'translation_weight': 10.0,
                    'rotation_weight': 15.0,
                    'max_iterations': 100
                }

            }]
        )
    
    bringup_dir = get_package_share_directory('navigation')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')


    # Config file
    lidar_nav2_param_file = os.path.join(bringup_dir,
                                   'config', 'nav2', 'nav2_lidar.yaml')

    nvblox_nav2_param_file = os.path.join(bringup_dir,
                                   'config', 'nav2', 'nav2_nvblox.yaml')

    nav2_param_file = PythonExpression([
        f"'{nvblox_nav2_param_file}' if '",
        use_nvblox,
        f"' == 'true' else '{lidar_nav2_param_file}'"
    ])

    # Nav2 launch
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')),
        launch_arguments={'use_sim_time': 'False',
                          'params_file': nav2_param_file,
                          'autostart': 'True'}.items())


    return LaunchDescription([nav2_launch, slam_toobox])
    
