# Navigation

This container runs the navigation of the robot (slam_toolbox, EKF, Nav2) and optionally various NVIDIA Isaac ROS packages, such as visual SLAM (https://nvidia-isaac-ros.github.io/v/release-3.2/repositories_and_packages/isaac_ros_visual_slam/isaac_ros_visual_slam/index.html) and NVBLOX (https://nvidia-isaac-ros.github.io/v/release-3.2/repositories_and_packages/isaac_ros_nvblox/index.html).

Started nodes:

- RealSense camera driver (always)
- EKF (`robot_localization`) fusing wheel odometry, IMU and VSLAM odometry (always)
- Isaac ROS visual SLAM (optional)
- NVBLOX 3D reconstruction and costmap (optional)
- slam_toolbox + Nav2 (optional)
- Foxglove bridge for visualization (always)

The setup targets a NVIDIA Jetson (aarch64, base image `nvcr.io/nvidia/isaac/ros:aarch64-ros2_humble_...`).

# Repository layout

| Path | Content |
| --- | --- |
| `src/packages/navigation` | Own package: launch files and configs, see [its README](src/packages/navigation/README.md). |
| `src/isaac_utils` | Isaac ROS sources (`isaac_ros_common`, `isaac_ros_nvblox`), cloned by `setup_isaac.sh`. Not part of this repository. |
| `.devcontainer` | Dockerfile, VS Code devcontainer and docker compose file. |

| Script | Runs on | Purpose |
| --- | --- | --- |
| `install_host.sh` | Host (root) | Builds and installs librealsense v2.55.1 from source. Also used inside the Dockerfile. |
| `setup_isaac.sh` | Devcontainer | Clones and builds the Isaac ROS packages (NVBLOX). |
| `setup.sh` | Devcontainer | Imports `src/packages/ros2.repos` and installs dependencies via rosdep. |
| `build.sh` | Devcontainer | Builds the own packages in `src/packages`. |
| `test.sh` | Devcontainer | Runs `colcon test`. |
| `entrypoint.sh` | Compose container | Starts the launch file with the selected features. |

The repository folder is mounted into both containers, so both share the same `build/` and `install/` folders:

- VS Code devcontainer: `/workspaces/navigation` (used for building)
- docker compose container: `/workspace` (used for running)

# Setup

## 1. Host prerequisites

- Jetson with JetPack, Docker and the NVIDIA container runtime
- VS Code with the "Dev Containers" extension
- `git-lfs` (the NVBLOX repository uses LFS files)
- librealsense on the host. If it is not installed yet, run once on the host:

  ```bash
  sudo ./install_host.sh
  rs-enumerate-devices   # should list the connected RealSense camera
  ```

  Attention: the script removes any existing librealsense installation in `/usr/local` before installing v2.55.1.

## 2. Open the devcontainer

Open the `navigation` folder in VS Code and select "Reopen in Container". The first image build takes a while, because librealsense and the realsense-ros wrapper (4.51.1) are compiled into `/opt/ros_ws`. All following steps are executed in the devcontainer terminal in `/workspaces/navigation`.

## 3. Build the Isaac ROS packages

The Isaac ROS packages have to be compiled locally for the platform. Visual SLAM is installed as apt package (`ros-humble-isaac-ros-visual-slam`) in the Dockerfile and does not need to be compiled. NVBLOX and its dependencies are built from source:

```bash
./setup_isaac.sh
```

The script

1. clones `isaac_ros_nvblox` (branch `release-3.2`, including submodules and `git lfs pull`) and `isaac_ros_common` (branch `release-3.2`) into `src/isaac_utils/`, if they do not exist yet,
2. enables the `realsense_splitter` package by removing its `COLCON_IGNORE`,
3. builds everything in `src/isaac_utils` into `install/` (merge install, `RelWithDebInfo`, `-DNVBLOX_ENABLE_REALSENSE=ON`).

**The compilation requires a lot of RAM and may crash** (the build is already running sequentially). Just restart `./setup_isaac.sh`: it uses `--packages-skip-build-finished` and continues with the packages that are not finished yet. You probably have to restart it several times. It helps to add swap and to stop other containers during the build.

## 4. Build the navigation package

```bash
./setup.sh   # load dependent repositories and install rosdep dependencies
./build.sh   # build src/packages into install/
```

The Isaac ROS packages from step 3 have to be built before, because the navigation package depends on them.

## 5. Adapt to your robot

VSLAM and navigation need a proper setup of the static transformations, especially from `base_link` / `base_footprint` to the camera and the lidar. Adapt the launch files and configs in `src/packages/navigation` (`config/filtering/ekf.yaml`, `config/nav2/*.yaml`, `config/nvblox/`) to the frames and dimensions of your own robot.

# Usage

## Start

Build and start the container from the `.devcontainer` folder:

```bash
cd .devcontainer
docker compose up --build      # add -d to run it in the background
```

The container runs `entrypoint.sh`, which sources `/opt/ros/humble`, `/opt/ros_ws/install` and `/workspace/install` and calls the launch file `navigation nvblox_nav.launch.py`. The features are selected via environment variables (default: all `true`):

| Variable | Feature |
| --- | --- |
| `USE_VSLAM` | Isaac ROS visual SLAM |
| `USE_NVBLOX` | NVBLOX 3D reconstruction and costmap |
| `USE_NAVIGATION` | slam_toolbox + EKF + Nav2 |

Examples:

```bash
# Lidar navigation only (Nav2 uses nav2_lidar.yaml)
USE_VSLAM=false USE_NVBLOX=false docker compose up --build

# VSLAM only, no mapping and navigation
USE_NVBLOX=false USE_NAVIGATION=false docker compose up --build
```

Stop the container with `Ctrl+C` or `docker compose down`. The launch process gets the stop signal directly (`init: true` + `exec`), so all nodes shut down cleanly.

## Required inputs

The container does not start the lidar and the motor control. These have to run in their own containers in the same ROS network (host network, `RMW_IMPLEMENTATION=rmw_cyclonedds_cpp`):

| Topic / TF | Source | Needed for |
| --- | --- | --- |
| `/scan` | Lidar | slam_toolbox, Nav2 |
| `/odom_wheel` | Motor control (wheel odometry) | EKF |
| `/camera0/gyro/sample` | RealSense (started here) | EKF |
| `/visual_slam/tracking/odometry` | VSLAM (started here) | EKF, if `USE_VSLAM=true` |
| TF `base_link` → lidar / camera frames | Static transformations | VSLAM, NVBLOX, slam_toolbox |

The EKF publishes `odom` → `base_footprint`, slam_toolbox publishes `map` → `odom`.

## Run manually in the devcontainer

For development the launch file can also be started in the devcontainer:

```bash
source /opt/ros/humble/setup.bash
source /opt/ros_ws/install/setup.bash
source /workspaces/navigation/install/setup.bash
ros2 launch navigation nvblox_nav.launch.py use_vslam:=true use_nvblox:=false use_navigation:=true
```

An overview of all launch files is in the [package README](src/packages/navigation/README.md).

## Visualization

The Foxglove bridge is started with the default port. Connect Foxglove Studio to `ws://<robot-ip>:8765`.

