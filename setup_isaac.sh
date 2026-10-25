#!/bin/bash
set -e

mkdir -p /workspaces/navigation/src/isaac_utils

if [ ! -d /workspaces/navigation/src/isaac_utils/isaac_ros_nvblox ]; then
        git clone --recurse-submodules -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_nvblox.git /workspaces/navigation/src/isaac_utils/isaac_ros_nvblox && \
                cd /workspaces/navigation/src/isaac_utils/isaac_ros_nvblox && \
                git lfs pull
        rm /workspaces/navigation/src/isaac_utils/isaac_ros_nvblox/nvblox_examples/realsense_splitter/COLCON_IGNORE
fi

if [ ! -d /workspaces/navigation/src/isaac_utils/isaac_ros_common ]; then
        git clone -b release-3.2 https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_common.git /workspaces/navigation/src/isaac_utils/isaac_ros_common
fi

if [ -f /workspaces/navigation/install/setup.bash ]; then
        source /workspaces/navigation/install/setup.bash
fi

# Set the default build type
BUILD_TYPE=RelWithDebInfo
colcon build \
        --base-paths /workspaces/navigation/src/isaac_utils \
        --merge-install \
        --executor sequential \
        --packages-skip-build-finished \
        --cmake-args "-DCMAKE_BUILD_TYPE=$BUILD_TYPE" "-DCMAKE_EXPORT_COMPILE_COMMANDS=On" "-DNVBLOX_ENABLE_REALSENSE=ON"  \
        -Wall -Wextra -Wpedantic
