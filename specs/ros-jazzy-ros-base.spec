%global ros_distro       jazzy
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-ros-base
Version:        0.13.1
Release:        1%{?dist}
Summary:        ROS 2 Jazzy default install — ros-core plus tf2 and common message types

# Aggregate of permissive-licensed runtime packages only — Phase 1 license rule.
License:        Apache-2.0 AND BSD-3-Clause
URL:            https://github.com/nickschuetz/ros2-rpm
Source0:        ros-jazzy-ros-base-%{version}.tar.gz

BuildArch:      noarch

# Pulls in the full ros_core (rclcpp, RMW + Fast DDS, message foundations)
Requires:       ros-jazzy-ros-core

# Workspace setup files (this is what makes `source /opt/ros/jazzy/setup.bash` work).
Requires:       ros-jazzy-ros-workspace
Requires:       ros-jazzy-ros-environment

# Python client library — needed for any Python ROS 2 development.
Requires:       ros-jazzy-rclpy

# tf2 stack — frame transforms, tf2_ros pubs / subs
Requires:       ros-jazzy-tf2
Requires:       ros-jazzy-tf2-msgs
Requires:       ros-jazzy-tf2-ros

# Phase 1 direct consumers — common message packages
Requires:       ros-jazzy-std-msgs
Requires:       ros-jazzy-geometry-msgs
Requires:       ros-jazzy-sensor-msgs
Requires:       ros-jazzy-nav-msgs
Requires:       ros-jazzy-trajectory-msgs
Requires:       ros-jazzy-action-msgs
Requires:       ros-jazzy-service-msgs

# Robotics-domain message packages used by O3DE + embedded consumers
Requires:       ros-jazzy-ackermann-msgs
Requires:       ros-jazzy-vision-msgs
Requires:       ros-jazzy-control-msgs

%description
Default install for ROS 2 Jazzy users. Pulls in ros-core (rclcpp, RMW/Fast DDS,
core message interfaces, component infrastructure) plus the tf2 transform
stack and the common message packages used by most robotics applications:
std_msgs, geometry_msgs, sensor_msgs, nav_msgs, trajectory_msgs, action_msgs,
service_msgs, ackermann_msgs, vision_msgs, and control_msgs.

License-clean: contains only Apache-2.0 and BSD-3-Clause content. The
Phase 2 dev-sandbox metapackage `ros-jazzy-ros-desktop` is a separate
opt-in install that adds the rqt suite (Qt/LGPL-3.0) and the Cyclone
DDS alternate RMW (EPL-2.0). The rviz2 chain is currently deferred in
both Phase 1 and Phase 2 — see docs/SCOPE.md.

%prep
# No source — pure metapackage.

%build
# Nothing to build.

%install
mkdir -p %{buildroot}%{install_prefix}
echo "ros-jazzy-ros-base %{version} (metapackage)" > %{buildroot}%{install_prefix}/.ros-base-version

%files
%{install_prefix}/.ros-base-version

%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 0.13.1-1
- Add ros-workspace, ros-environment, rclpy to the dependency set so a
  fresh `dnf install ros-jazzy-ros-base` results in a usable Python +
  C++ ROS environment with /opt/ros/jazzy/setup.bash present.
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 0.13.0-1
- Initial Phase 1 ros-base metapackage covering tf2 + common message stack.
