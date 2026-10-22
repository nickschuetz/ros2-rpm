%global ros_distro       lyrical
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-o3de-gem-deps
Version:        1.0.0
Release:        1%{?dist}
Summary:        ROS 2 Lyrical packages needed by the O3DE ROS 2 Gems

# Aggregate of permissive-licensed packages only (ADR 0003, ADR 0014).
License:        Apache-2.0 AND BSD-3-Clause
URL:            https://github.com/nickschuetz/ros2-rpm

BuildArch:      noarch

# Core install: rclcpp, the default RMW (Fast DDS) and the workspace setup
# files that the O3DE launcher sources from /opt/ros/lyrical.
Requires:       ros-lyrical-ros-core
Requires:       ros-lyrical-ros-workspace
Requires:       ros-lyrical-ros-environment
Requires:       ros-lyrical-rmw-fastrtps-cpp

# Exactly the packages the o3de-extras Gems pass to
# target_depends_on_ros2_packages() (ROS2, ROS2Sensors, ROS2Controllers,
# SimulationInterfaces), so a project using them configures and links.
Requires:       ros-lyrical-rclcpp
Requires:       ros-lyrical-rclcpp-action
Requires:       ros-lyrical-builtin-interfaces
Requires:       ros-lyrical-std-msgs
Requires:       ros-lyrical-geometry-msgs
Requires:       ros-lyrical-sensor-msgs
Requires:       ros-lyrical-nav-msgs
Requires:       ros-lyrical-tf2-ros
Requires:       ros-lyrical-ackermann-msgs
Requires:       ros-lyrical-vision-msgs
Requires:       ros-lyrical-control-msgs
Requires:       ros-lyrical-simulation-interfaces

# The ros2 CLI, for checking topics and services from a running simulation.
# Weak dependencies so a headless or CI install can skip them.
Recommends:     ros-lyrical-ros2cli
Recommends:     ros-lyrical-ros2topic
Recommends:     ros-lyrical-ros2node
Recommends:     ros-lyrical-ros2service
Recommends:     ros-lyrical-ros2run
Recommends:     ros-lyrical-ros2launch
Recommends:     ros-lyrical-ros2interface
Recommends:     ros-lyrical-ros2param
Recommends:     ros-lyrical-ros2action

%description
Not the official ROS 2 packages for Fedora.

Installs the ROS 2 Lyrical packages that the O3DE ROS 2 Gems (ROS2,
ROS2Sensors, ROS2Controllers, SimulationInterfaces from o3de-extras)
build and run against: rclcpp, rclcpp_action, the Fast DDS RMW, tf2_ros,
builtin_interfaces, std_msgs, geometry_msgs, sensor_msgs, nav_msgs,
ackermann_msgs, vision_msgs, control_msgs and simulation_interfaces. The
ros2 command line tools are recommended, not required.

The Gazebo message package is not included: it has no Lyrical release, and
the Gems build without it (their optional Gazebo message support stays off).

Lyrical support in the Gems requires o3de-extras from the 26.10 line
(stabilization/26100) or newer. For O3DE 26.05, use the Jazzy COPR.

%prep
# No source, pure metapackage.

%build
# Nothing to build.

%install
mkdir -p %{buildroot}%{install_prefix}
echo "ros-lyrical-o3de-gem-deps %{version} (metapackage)" > %{buildroot}%{install_prefix}/.o3de-gem-deps-version

%files
%{install_prefix}/.o3de-gem-deps-version

%changelog
* Fri Oct 16 2026 Nick Schuetz <nschuetz@redhat.com> - 1.0.0-1
- Initial metapackage for the O3DE ROS 2 Gems: the packages the Gems link
  against, simulation_interfaces, the Fast DDS RMW, and the ros2 CLI as
  weak dependencies (ADR 0014).
