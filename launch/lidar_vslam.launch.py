from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription

from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import PathJoinSubstitution

from launch_ros.actions import ComposableNodeContainer, Node
from launch_ros.descriptions import ComposableNode


import os
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():

    """Launch file which brings up visual slam node configured for RealSense."""
    realsense_camera_node = Node(
        name='camera',
        namespace='camera',
        package='realsense2_camera',
        executable='realsense2_camera_node',
        parameters=[{
            'enable_infra1': True,
            'enable_infra2': True,
            'enable_color': False,
            'enable_depth': False,
            'depth_module.emitter_enabled': 0,
            'depth_module.profile': '640x360x90',
            'enable_gyro': True,
            'enable_accel': True,
            'gyro_fps': 200,
            'accel_fps': 200,
            'unite_imu_method': 2
        }],
    )

    visual_slam_node = ComposableNode(
        name='visual_slam_node',
        package='isaac_ros_visual_slam',
        plugin='nvidia::isaac_ros::visual_slam::VisualSlamNode',
        parameters=[{
            'enable_image_denoising': False,
            'rectified_images': True,
            'enable_imu_fusion': False,
            'gyro_noise_density': 0.000244,
            'gyro_random_walk': 0.000019393,
            'accel_noise_density': 0.001862,
            'accel_random_walk': 0.003,
            'calibration_frequency': 200.0,
            'image_jitter_threshold_ms': 22.00,
            'base_frame': 'base_footprint',
            'imu_frame': 'camera_gyro_optical_frame',
            'enable_slam_visualization': True,
            'enable_landmarks_view': True,
            'enable_observations_view': True,
            'enable_ground_constraint_in_odometry': True,
            'enable_ground_constraint_in_slam': True,
            'enable_localization_n_mapping': False,
            'publish_map_to_odom_tf': False,
            'publish_odom_to_base_tf': False,
            'camera_optical_frames': [
                'camera_infra1_optical_frame',
                'camera_infra2_optical_frame',
            ],
        }],
        remappings=[
            ('visual_slam/image_0', 'camera/infra1/image_rect_raw'),
            ('visual_slam/camera_info_0', 'camera/infra1/camera_info'),
            ('visual_slam/image_1', 'camera/infra2/image_rect_raw'),
            ('visual_slam/camera_info_1', 'camera/infra2/camera_info'),
            ('visual_slam/imu', 'camera/imu'),
        ],
    )

    visual_slam_launch_container = ComposableNodeContainer(
        name='visual_slam_launch_container',
        namespace='',
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=[visual_slam_node],
        output='screen',
    )

    # trans_map_odom = Node(
    #         package='tf2_ros',
    #         executable='static_transform_publisher',
    #         name='map_to_odom',
    #         arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
    #     )
    
    # imu_frame = Node(
    #         package='tf2_ros',
    #         executable='static_transform_publisher',
    #         name='base_footprint_to_base_link',
    #         arguments=['0', '0', '0', '0', '0', '0', 'camera_gyro_frame', 'camera_imu_optical_frame']
    #     )
    
    slam_toobox = Node(
            package='slam_toolbox',
            # executable='sync_slam_toolbox_node',   # or 'async_slam_toolbox_node'
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[{
                'resolution': 0.03,
                'map_update_interval': 0.1,
                'use_sim_time': False,
                'use_odometry': True,
                'odom_frame': 'base_footprint',
                'odom_frame': 'odom',         # <--- your odometry frame
                'map_frame': 'map',
                'base_frame': 'base_footprint',
                'scan_topic': '/scan',
                'mode': 'mapping',              # or 'localization'
                'tf_buffer_duration': 10.0,
                'transform_timeout': 0.5,
                'min_laser_range': 0.2,   # the minimum range your Lidar can measure
                'max_laser_range': 12.0  # the maximum range your Lidar can measure

            }]
        )
    
    bringup_dir = get_package_share_directory('launch_robot')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    # Config file
    nav2_param_file = os.path.join(bringup_dir,
                                   'config', 'nav2', 'nav2_lidar.yaml')

    # Nav2 launch
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'navigation_launch.py')),
        launch_arguments={'use_sim_time': 'False',
                          'params_file': nav2_param_file,
                          'autostart': 'True'}.items())

    ekf_param_file = os.path.join(bringup_dir,
                                   'config', 'filtering', 'ekf.yaml')

    ekf_smooting = Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[ekf_param_file]
        )

    #return LaunchDescription([ekf_smooting])
    #return LaunchDescription([ekf_smooting, visual_slam_launch_container, realsense_camera_node])
    #return LaunchDescription([ekf_smooting, nav2_launch, imu_frame, slam_toobox, visual_slam_launch_container, realsense_camera_node])
    return LaunchDescription([ekf_smooting, nav2_launch, slam_toobox, visual_slam_launch_container, realsense_camera_node])
    #return LaunchDescription([visual_slam_launch_container, realsense_camera_node])
    #return LaunchDescription([trans_map_odom, slam_toobox, visual_slam_launch_container, realsense_camera_node])
    #return LaunchDescription([nav2_launch, trans_map_odom, slam_toobox, visual_slam_launch_container, realsense_camera_node])
    
