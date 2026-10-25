#!/bin/bash
# Container entrypoint: select the features via environment variables and hand over to the ROS launch file.
# Feature logic lives in src/packages/navigation/launch/nvblox_nav.launch.py.
set -eo pipefail

# Source ROS environments
source /opt/ros/humble/setup.bash
source /opt/ros_ws/install/setup.bash
source /workspace/install/setup.bash

USE_VSLAM="${USE_VSLAM:-true}"              # true / false: Isaac ROS visual SLAM
USE_NVBLOX="${USE_NVBLOX:-true}"            # true / false: NVBLOX 3D reconstruction and costmap
USE_NAVIGATION="${USE_NAVIGATION:-true}"    # true / false: slam_toolbox + EKF + Nav2

echo "=============================================="
echo "  Navigation Container Startup"
echo "  VSLAM:      ${USE_VSLAM}"
echo "  NVBLOX:     ${USE_NVBLOX}"
echo "  Navigation: ${USE_NAVIGATION}"
echo "=============================================="

# exec: ros2 launch becomes the main process, so docker stop shuts all nodes down cleanly
exec ros2 launch navigation nvblox_nav.launch.py \
    use_vslam:="${USE_VSLAM}" \
    use_nvblox:="${USE_NVBLOX}" \
    use_navigation:="${USE_NAVIGATION}"
