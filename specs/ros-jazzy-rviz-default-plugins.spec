%global ros_distro       jazzy
%global pkg_name         rviz_default_plugins
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rviz-default-plugins
Version:        14.1.20
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rviz_default_plugins

License:        BSD-3-Clause
URL:            https://github.com/ros2/rviz/blob/ros2/README.md
Source0:        https://github.com/ros2-gbp/rviz-release/archive/refs/tags/release/jazzy/rviz_default_plugins/14.1.20-2.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  ros-jazzy-ament-cmake-ros
BuildRequires:  ros-jazzy-geometry-msgs
BuildRequires:  ros-jazzy-nav-msgs
BuildRequires:  ros-jazzy-pluginlib
BuildRequires:  ros-jazzy-rclcpp
BuildRequires:  ros-jazzy-rviz-common
BuildRequires:  ros-jazzy-rviz-ogre-vendor
BuildRequires:  ros-jazzy-rviz-rendering
BuildRequires:  ros-jazzy-tf2
BuildRequires:  ros-jazzy-tf2-ros

Requires:       qt5-qtbase
Requires:       qt5-qtbase-gui
Requires:       ros-jazzy-geometry-msgs
Requires:       ros-jazzy-nav-msgs
Requires:       ros-jazzy-pluginlib
Requires:       ros-jazzy-rclcpp
Requires:       ros-jazzy-rviz-common
Requires:       ros-jazzy-rviz-ogre-vendor
Requires:       ros-jazzy-rviz-rendering
Requires:       ros-jazzy-tf2
Requires:       ros-jazzy-tf2-ros

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Several default plugins for rviz to cover the basic functionality.

%prep
%autosetup -p1 -n rviz-release-release-jazzy-rviz_default_plugins-14.1.20-2

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
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 14.1.20-1
- Initial Fedora COPR build for ROS 2 Jazzy.
