%global ros_distro       jazzy
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-ros-core
Version:        0.13.0
Release:        1%{?dist}
Summary:        ROS 2 Jazzy core libraries and runtime

# Aggregate of permissive-licensed runtime packages only, Phase 1 license rule.
License:        Apache-2.0 AND BSD-3-Clause
URL:            https://github.com/nickschuetz/ros2-rpm
Source0:        ros-jazzy-ros-core-%{version}.tar.gz

BuildArch:      noarch

# Core client library
Requires:       ros-jazzy-rclcpp

# Core RMW + Fast DDS default
Requires:       ros-jazzy-rmw-implementation
Requires:       ros-jazzy-rmw-fastrtps-cpp

# Core message foundations
Requires:       ros-jazzy-builtin-interfaces
Requires:       ros-jazzy-rcl-interfaces
Requires:       ros-jazzy-rosgraph-msgs

# Core extension points used by ros-jazzy-* clients
Requires:       ros-jazzy-rclcpp-action
Requires:       ros-jazzy-rclcpp-components
Requires:       ros-jazzy-rcl-action
Requires:       ros-jazzy-class-loader
Requires:       ros-jazzy-message-filters
Requires:       ros-jazzy-rcl-logging-spdlog
Requires:       ros-jazzy-libstatistics-collector

# Setup environment
Provides:       ros-jazzy-setup-env

%description
Metapackage that pulls in the runtime client library (rclcpp), the default
RMW implementation (Fast DDS), the core message interfaces, and lifecycle/
component infrastructure. Equivalent to upstream ROS 2 Jazzy `ros_core`.

This is the minimal-runtime install. For tf2 + sensor / nav messages,
install ros-jazzy-ros-base instead.

%prep
# No source, pure metapackage.

%build
# Nothing to build.

%install
mkdir -p %{buildroot}%{install_prefix}
# A trivial sentinel so debuginfo machinery has something to inspect.
echo "ros-jazzy-ros-core %{version} (metapackage)" > %{buildroot}%{install_prefix}/.ros-core-version

%files
%{install_prefix}/.ros-core-version

%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 0.13.0-1
- Initial Phase 1 ros-core metapackage.
