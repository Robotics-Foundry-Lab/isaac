# isaac
Launch files for the robot platform within the Isaac ROS container. They depend on Isaac ROS packages (`isaac_ros_launch_utils`, NVBLOX, VSLAM) and therefore only run inside this container.

## Launch files

| File | Purpose |
| --- | --- |
| `launch/nvblox_nav.launch.py` | Main entry point (used by `entrypoint.sh`). Arguments `use_vslam`, `use_nvblox`, `use_navigation` enable/disable the features. Also starts the EKF (`config/filtering/ekf.yaml`: wheel odometry, VSLAM odometry, IMU). |
| `launch/lidar_nav.launch.py` | Navigation layer of the Isaac stack, included by `nvblox_nav.launch.py`: slam_toolbox + Nav2. Uses `nav2_nvblox.yaml` if `use_nvblox:=true`, otherwise `nav2_lidar.yaml`. |
| `launch/sensors/realsense.launch.py` | RealSense camera incl. emitter splitter. |
| `launch/perception/vslam.launch.py` | Isaac ROS visual SLAM. |
| `launch/perception/nvblox.launch.py` | NVBLOX 3D reconstruction / costmap. |
| `launch/nav2/nav2_realsense.launch.py` | Unused and currently broken: references `config/nav2/nav2_realsense.yaml`, which no longer exists. |
| `launch/visualization/*.launch.py` | Foxglove bridge / visualization. |

## Relation to the `navigation` repository
A standalone lidar navigation without any Isaac dependencies (slam_toolbox + EKF with wheel odometry and IMU only) lives in the `navigation` repository (`robot_navigation` package). Both variants are maintained separately on purpose: changes to footprint, inflation or EKF settings have to be applied to both if they should stay in sync.
