%global ros_distro       lyrical
%global pkg_name         point_cloud_transport
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-point-cloud-transport
Version:        5.4.2
Release:        1%{?dist}
Summary:        ROS 2 Lyrical point_cloud_transport

License:        BSD-3-Clause
URL:            https://github.com/ros-perception/point_cloud_transport
Source0:        https://github.com/ros2-gbp/point_cloud_transport-release/archive/refs/tags/release/lyrical/point_cloud_transport/5.4.2-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-lyrical-ament-cmake-gen-version-h
BuildRequires:  ros-lyrical-ament-cmake-ros
BuildRequires:  ros-lyrical-ament-cmake-ros-core
BuildRequires:  ros-lyrical-message-filters
BuildRequires:  ros-lyrical-pluginlib
BuildRequires:  ros-lyrical-rclcpp
BuildRequires:  ros-lyrical-rclcpp-components
BuildRequires:  ros-lyrical-rcpputils
BuildRequires:  ros-lyrical-rmw
BuildRequires:  ros-lyrical-sensor-msgs
BuildRequires:  tinyxml2-devel

Requires:       ros-lyrical-message-filters
Requires:       ros-lyrical-pluginlib
Requires:       ros-lyrical-rclcpp
Requires:       ros-lyrical-rclcpp-components
Requires:       ros-lyrical-rcpputils
Requires:       ros-lyrical-rmw
Requires:       ros-lyrical-sensor-msgs
Requires:       tinyxml2-devel

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Support for transporting PointCloud2 messages in compressed format and
plugin interface for implementing additional PointCloud2 transports.

%prep
%autosetup -p1 -n point_cloud_transport-release-release-lyrical-point_cloud_transport-5.4.2-1

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
# Ships the main lib plus a plugins lib and a pc_republish_node component lib,
# and the list_transports / republish executables under lib/point_cloud_transport/.
%{install_prefix}/lib/lib*.so*
%{install_prefix}/lib/%{pkg_name}/


%changelog
* Thu Jun 04 2026 Nick Schuetz <nschuetz@redhat.com> - 5.4.2-1
- Initial Fedora COPR build for ROS 2 Lyrical.
