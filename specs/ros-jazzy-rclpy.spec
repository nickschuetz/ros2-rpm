%global ros_distro       jazzy
%global pkg_name         rclpy
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rclpy
Version:        7.1.9
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rclpy

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/rclpy-release
Source0:        https://github.com/ros2-gbp/rclpy-release/archive/refs/tags/release/jazzy/rclpy/7.1.9-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake
BuildRequires:  ros-jazzy-lifecycle-msgs
BuildRequires:  ros-jazzy-pybind11-vendor
BuildRequires:  ros-jazzy-python-cmake-module
BuildRequires:  ros-jazzy-rcl
BuildRequires:  ros-jazzy-rcl-action
BuildRequires:  ros-jazzy-rcl-interfaces
BuildRequires:  ros-jazzy-rcl-lifecycle
BuildRequires:  ros-jazzy-rcl-logging-interface
BuildRequires:  ros-jazzy-rcl-yaml-param-parser
BuildRequires:  ros-jazzy-rcpputils
BuildRequires:  ros-jazzy-rcutils
BuildRequires:  ros-jazzy-rmw
BuildRequires:  ros-jazzy-rmw-implementation
BuildRequires:  ros-jazzy-rmw-implementation-cmake
BuildRequires:  ros-jazzy-rosidl-runtime-c
BuildRequires:  ros-jazzy-unique-identifier-msgs

Requires:       python3-PyYAML
Requires:       ros-jazzy-action-msgs
Requires:       ros-jazzy-ament-index-python
Requires:       ros-jazzy-builtin-interfaces
Requires:       ros-jazzy-lifecycle-msgs
Requires:       ros-jazzy-rcl
Requires:       ros-jazzy-rcl-action
Requires:       ros-jazzy-rcl-interfaces
Requires:       ros-jazzy-rcl-lifecycle
Requires:       ros-jazzy-rcl-logging-interface
Requires:       ros-jazzy-rcl-yaml-param-parser
Requires:       ros-jazzy-rmw
Requires:       ros-jazzy-rmw-implementation
Requires:       ros-jazzy-rosgraph-msgs
Requires:       ros-jazzy-rosidl-runtime-c
Requires:       ros-jazzy-rpyutils
Requires:       ros-jazzy-unique-identifier-msgs

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Package containing the Python client.

%prep
%autosetup -p1 -n rclpy-release-release-jazzy-rclpy-7.1.9-1

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
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}-py%{python3_version}.egg-info/
%{install_prefix}/lib/lib%{pkg_name}.so*


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 7.1.9-1
- Initial Fedora COPR build for ROS 2 Jazzy.
