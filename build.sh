#!/bin/bash
set -e

# Set the default build type
BUILD_TYPE=RelWithDebInfo
colcon build \
        --base-paths /workspaces/navigation/src/packages \
        --merge-install \
        --executor sequential \
        --cmake-args "-DCMAKE_BUILD_TYPE=$BUILD_TYPE" "-DCMAKE_EXPORT_COMPILE_COMMANDS=On" "-DNVBLOX_ENABLE_REALSENSE=ON"  \
        -Wall -Wextra -Wpedantic
