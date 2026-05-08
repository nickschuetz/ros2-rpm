%global ros_distro       jazzy
%global pkg_name         tf2_ros
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-tf2-ros
Version:        0.36.9
Release:        1%{?dist}
Summary:        ROS 2 Jazzy tf2_ros

License:        BSD-3-Clause
URL:            http://www.ros.org/wiki/tf2_ros
Source0:        https://github.com/ros2-gbp/geometry2-release/archive/refs/tags/release/jazzy/tf2_ros/0.36.9-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake
BuildRequires:  ros-jazzy-builtin-interfaces
BuildRequires:  ros-jazzy-geometry-msgs
BuildRequires:  ros-jazzy-message-filters
BuildRequires:  ros-jazzy-rcl-interfaces
BuildRequires:  ros-jazzy-rclcpp
BuildRequires:  ros-jazzy-rclcpp-action
BuildRequires:  ros-jazzy-rclcpp-components
BuildRequires:  ros-jazzy-tf2
BuildRequires:  ros-jazzy-tf2-msgs

Requires:       ros-jazzy-builtin-interfaces
Requires:       ros-jazzy-geometry-msgs
Requires:       ros-jazzy-message-filters
Requires:       ros-jazzy-rcl-interfaces
Requires:       ros-jazzy-rclcpp
Requires:       ros-jazzy-rclcpp-action
Requires:       ros-jazzy-rclcpp-components
Requires:       ros-jazzy-tf2
Requires:       ros-jazzy-tf2-msgs

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
This package contains the C++ ROS bindings for the tf2 library

%prep
%autosetup -p1 -n geometry2-release-release-jazzy-tf2_ros-0.36.9-1

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
    -DAMENT_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_INSTALL_INCLUDEDIR=include \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DCMAKE_INSTALL_BINDIR=bin \
    -DCMAKE_INSTALL_DATADIR=share \
    -DCMAKE_INSTALL_SYSCONFDIR=etc \
    -DINCLUDE_INSTALL_DIR=%{install_prefix}/include \
    -DLIB_INSTALL_DIR=%{install_prefix}/lib \
    -DSYSCONF_INSTALL_DIR=%{install_prefix}/etc \
    -DSHARE_INSTALL_PREFIX=%{install_prefix}/share \
    -DSETUPTOOLS_DEB_LAYOUT=OFF -DBUILD_TESTING=OFF
%cmake_build


%install
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
%cmake_install


%check
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
echo 'tests skipped — see CLAUDE.md / packages.yaml'

%files
# (no LICENSE file in source tree — see package.xml <license>)
%doc CHANGELOG.rst
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
%{install_prefix}/share/%{pkg_name}/
# Sentinels: ament_index/resource_index/<index>/<pkg>. Glob covers
# packages/, package_run_dependencies/, parent_prefix_path/, and any
# member_of_group entries (rosidl_runtime_packages, etc.).
%{install_prefix}/share/ament_index/resource_index/*/%{pkg_name}
%{install_prefix}/include/%{pkg_name}/
%{install_prefix}/lib/lib%{pkg_name}.so*
%{install_prefix}/lib/libstatic_transform_broadcaster_node.so*
# CLI executables (buffer_server, static_transform_publisher, tf2_echo, tf2_monitor)
%{install_prefix}/lib/%{pkg_name}/


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 0.36.9-1
- Initial Fedora COPR build for ROS 2 Jazzy.
