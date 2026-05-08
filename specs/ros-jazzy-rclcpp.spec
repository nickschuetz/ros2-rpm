%global ros_distro       jazzy
%global pkg_name         rclcpp
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rclcpp
Version:        28.1.18
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rclcpp

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/rclcpp-release
Source0:        https://github.com/ros2-gbp/rclcpp-release/archive/refs/tags/release/jazzy/rclcpp/28.1.18-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake-gen-version-h
BuildRequires:  ros-jazzy-ament-cmake-ros
BuildRequires:  ros-jazzy-ament-index-cpp
BuildRequires:  ros-jazzy-builtin-interfaces
BuildRequires:  ros-jazzy-libstatistics-collector
BuildRequires:  ros-jazzy-rcl
BuildRequires:  ros-jazzy-rcl-interfaces
BuildRequires:  ros-jazzy-rcl-logging-interface
BuildRequires:  ros-jazzy-rcl-yaml-param-parser
BuildRequires:  ros-jazzy-rcpputils
BuildRequires:  ros-jazzy-rcutils
BuildRequires:  ros-jazzy-rmw
BuildRequires:  ros-jazzy-rosgraph-msgs
BuildRequires:  ros-jazzy-rosidl-dynamic-typesupport
BuildRequires:  ros-jazzy-rosidl-runtime-c
BuildRequires:  ros-jazzy-rosidl-runtime-cpp
BuildRequires:  ros-jazzy-rosidl-typesupport-c
BuildRequires:  ros-jazzy-rosidl-typesupport-cpp
BuildRequires:  ros-jazzy-statistics-msgs
BuildRequires:  ros-jazzy-tracetools

Requires:       ros-jazzy-ament-index-cpp
Requires:       ros-jazzy-builtin-interfaces
Requires:       ros-jazzy-libstatistics-collector
Requires:       ros-jazzy-rcl
Requires:       ros-jazzy-rcl-interfaces
Requires:       ros-jazzy-rcl-logging-interface
Requires:       ros-jazzy-rcl-yaml-param-parser
Requires:       ros-jazzy-rcpputils
Requires:       ros-jazzy-rcutils
Requires:       ros-jazzy-rmw
Requires:       ros-jazzy-rosgraph-msgs
Requires:       ros-jazzy-rosidl-dynamic-typesupport
Requires:       ros-jazzy-rosidl-runtime-c
Requires:       ros-jazzy-rosidl-runtime-cpp
Requires:       ros-jazzy-rosidl-typesupport-c
Requires:       ros-jazzy-rosidl-typesupport-cpp
Requires:       ros-jazzy-statistics-msgs
Requires:       ros-jazzy-tracetools

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
The ROS client library in C++.

%prep
%autosetup -p1 -n rclcpp-release-release-jazzy-rclcpp-28.1.18-1

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


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 28.1.18-1
- Initial Fedora COPR build for ROS 2 Jazzy.
