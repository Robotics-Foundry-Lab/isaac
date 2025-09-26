# SPDX-FileCopyrightText: NVIDIA CORPORATION & AFFILIATES
# Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from isaac_ros_launch_utils.all_types import *
import isaac_ros_launch_utils as lu

from nvblox_ros_python_utils.nvblox_launch_utils import NvbloxMode, NvbloxCamera, NvbloxPeopleSegmentation
from nvblox_ros_python_utils.nvblox_constants import NVBLOX_CONTAINER_NAME


def generate_launch_description() -> LaunchDescription:
    args = lu.ArgumentContainer()
    args.add_arg('log_level', 'info', choices=[
                 'debug', 'info', 'warn'], cli=True)
    args.add_arg(
        'mode',
        default=NvbloxMode.static,
        choices=NvbloxMode.names(),
        description='The nvblox mode.',
        cli=True)
    args.add_arg(
        'people_segmentation',
        default=NvbloxPeopleSegmentation.peoplesemsegnet_vanilla,
        choices=[
            str(NvbloxPeopleSegmentation.peoplesemsegnet_vanilla),
            str(NvbloxPeopleSegmentation.peoplesemsegnet_shuffleseg)
        ],
        description='The  model type of PeopleSemSegNet (only used when mode:=people_segmentation).',
        cli=True)
    actions = args.get_launch_actions()

    # Single realsense
    camera_mode = NvbloxCamera.realsense

    actions.append(
        lu.include(
            'launch_robot',
            'launch/sensors/realsense.launch.py',
            launch_arguments={
                'camera_serial_numbers': '',
                'num_cameras': 1,
            }))

    # Visual SLAM
    actions.append(
        lu.include(
            'launch_robot',
            'launch/perception/vslam.launch.py',
            launch_arguments={
                'container_name': NVBLOX_CONTAINER_NAME,
                'camera': camera_mode,
            },
            # Delay for 1 second to make sure that the static topics from the rosbag are published.
            delay=1.0,
        ))

    # Nvblox
    actions.append(
        lu.include(
            'launch_robot',
            'launch/perception/nvblox.launch.py',
            launch_arguments={
                'mode': 'static',
                'camera': camera_mode,
                'num_cameras': 1,
            }))

    # Visualization
    actions.append(
        lu.include(
            'launch_robot',
            'launch/visualization/visualization.launch.py',
            launch_arguments={
                'mode': args.mode,
                'camera': camera_mode,
                'use_foxglove_whitelist': False,
            }))

    actions.append(
        lu.component_container(
            NVBLOX_CONTAINER_NAME,
            log_level=args.log_level))

    # Nav2 
    actions.append(
        lu.include(
            'launch_robot',
            'launch/nav2/nav2_realsense.launch.py'))

    return LaunchDescription(actions)
