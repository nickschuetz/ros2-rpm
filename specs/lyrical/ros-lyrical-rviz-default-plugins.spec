%global ros_distro       lyrical
%global pkg_name         rviz_default_plugins
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-rviz-default-plugins
Version:        15.2.3
Release:        1%{?dist}
Summary:        ROS 2 Lyrical rviz_default_plugins

License:        BSD-3-Clause
URL:            https://github.com/ros2/rviz/blob/ros2/README.md
Source0:        https://github.com/ros2-gbp/rviz-release/archive/refs/tags/release/lyrical/rviz_default_plugins/15.2.3-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  ros-lyrical-ament-cmake-ros
BuildRequires:  ros-lyrical-geometry-msgs
BuildRequires:  ros-lyrical-nav-msgs
BuildRequires:  ros-lyrical-pluginlib
BuildRequires:  ros-lyrical-rclcpp
BuildRequires:  ros-lyrical-rviz-common
BuildRequires:  ros-lyrical-rviz-ogre-vendor
BuildRequires:  ros-lyrical-rviz-rendering
BuildRequires:  ros-lyrical-tf2
BuildRequires:  ros-lyrical-tf2-ros

Requires:       qt6-qtbase
Requires:       qt6-qtbase-gui
Requires:       ros-lyrical-geometry-msgs
Requires:       ros-lyrical-nav-msgs
Requires:       ros-lyrical-pluginlib
Requires:       ros-lyrical-rclcpp
Requires:       ros-lyrical-rviz-common
Requires:       ros-lyrical-rviz-ogre-vendor
Requires:       ros-lyrical-rviz-rendering
Requires:       ros-lyrical-tf2
Requires:       ros-lyrical-tf2-ros

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Several default plugins for rviz to cover the basic functionality.

%prep
%autosetup -p1 -n rviz-release-release-lyrical-rviz_default_plugins-15.2.3-1

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
echo 'tests skipped (see CLAUDE.md / packages.yaml)'

%files
# (no LICENSE file in source tree; see package.xml <license>)
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
* Wed Jun 03 2026 Nick Schuetz <nschuetz@redhat.com> - 15.2.3-1
- Initial Fedora COPR build for ROS 2 Lyrical.
