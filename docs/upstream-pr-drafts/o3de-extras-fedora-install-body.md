## What

Adds a Fedora 44+ / CentOS Stream 10 install path for the ROS 2 Gem in the README's "Platform" section. Three-line `dnf` block users can copy/paste, plus a one-line context note about where the COPR sits relative to the upcoming official Fedora support for Lyrical Luth.

## Why

Currently the README says the Gem is tested on Ubuntu 22.04 only. Fedora users have no obvious pointer to a working ROS 2 Jazzy install path. The [`hellaenergy/ros2`](https://copr.fedorainfracloud.org/coprs/hellaenergy/ros2) COPR fills that gap and packages every direct dep the Gem `find_package`s, including the optional `gazebo_msgs` that gates `ContactSensor` and `ROS 2 Spawner`. It's positioned as a development-only sandbox until the official Fedora ROS 2 packages land for Lyrical.

## Verified

I'm the maintainer of the COPR. End-to-end smoke test on Fedora 44 (GCC 15.1.1, Python 3.14, CMake 4.0.3) covers:

- All 9 required Gem deps (`rclcpp`, `builtin_interfaces`, `control_msgs`, `geometry_msgs`, `std_msgs`, `sensor_msgs`, `nav_msgs`, `tf2_ros`, `ackermann_msgs`, `vision_msgs`).
- Optional `gazebo_msgs` (BSD-3-Clause).
- Both Fast DDS (default) and Cyclone DDS as RMW implementations.
- C++ rclcpp build + run, Python rclpy import, `ros2 topic list`, `demo_nodes_cpp/talker` publishing.

Smoke test script and full per-section coverage: <https://github.com/nickschuetz/ros2-rpm/blob/main/scripts/smoke-test.sh>.

## Scope of this PR

Documentation only. No build system changes. No claim that maintainers test on Fedora; the wording is "available via the third-party COPR" so the Gem's testing matrix is unaffected.
