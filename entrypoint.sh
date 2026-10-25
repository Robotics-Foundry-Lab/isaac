# echo "Starting nodes"

source /opt/ros/humble/setup.bash
source /opt/ros_ws/install/setup.bash
source /workspace/install/setup.bash
ros2 launch isaac nvblox_nav.launch.py use_vslam:=true use_nvblox:=true use_navigation:=true