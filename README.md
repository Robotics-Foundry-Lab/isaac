# Isaac

This container controls various NVIDIA Isaac ros packages, such as visual slam (https://nvidia-isaac-ros.github.io/v/release-3.2/repositories_and_packages/isaac_ros_visual_slam/isaac_ros_visual_slam/index.html) and NVBLOX (https://nvidia-isaac-ros.github.io/v/release-3.2/repositories_and_packages/isaac_ros_nvblox/index.html).

# Prerequisites

1. If you did not yet install the realsense library on the host you have to execute install_host.sh on the host.
2. The Isaac ROS packages have to be compiled locally for the platform by using the "setup_isaac.sh" script. The compilation requires a lot of RAM, which means that it may crashes during the compilation. You probably have to restart it several times as it will store the progress. (In the future we will provide a prepared docker file that has this dependency already).
3. Run setup.sh to load dependent repositories
4. Run build.sh to build the repositories
5. The VSlam and Navigation need a proper setup of the static transformations, especially to the camera and the lidar. You may adapt the launch files to the frames of your own robot.

# Usage

You can build and start the container in the ".devcontainer" folder via "docker compose up --build". In the docker-compose.yml the entrypoint is defined for the container. The default is the "entry_point.sh", which can start NVBLOX, VSlam and navigation. If you look into the entry_point.sh you can see that a launch file "isaac nvblox_nav.launch.py" is called. If you want to start indepedent features, such as NVBLOX, VSlam etc. you can select or deselect those features.