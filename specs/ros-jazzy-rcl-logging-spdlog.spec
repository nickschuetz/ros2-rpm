%global ros_distro       jazzy
%global pkg_name         rcl_logging_spdlog
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rcl-logging-spdlog
Version:        3.1.1
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rcl_logging_spdlog

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/rcl_logging-release
Source0:        https://github.com/ros2-gbp/rcl_logging-release/archive/refs/tags/release/jazzy/rcl_logging_spdlog/3.1.1-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake-ros
BuildRequires:  ros-jazzy-rcl-logging-interface
BuildRequires:  ros-jazzy-rcpputils
BuildRequires:  ros-jazzy-rcutils
BuildRequires:  ros-jazzy-spdlog-vendor
BuildRequires:  spdlog-devel

Requires:       ros-jazzy-rcl-logging-interface
Requires:       ros-jazzy-rcpputils
Requires:       ros-jazzy-rcutils
Requires:       ros-jazzy-spdlog-vendor
Requires:       spdlog-devel

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Implementation of rcl_logging API for an spdlog backend.

%prep
%autosetup -p1 -n rcl_logging-release-release-jazzy-rcl_logging_spdlog-3.1.1-1

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
%{install_prefix}/lib/lib%{pkg_name}.so*


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 3.1.1-1
- Initial Fedora COPR build for ROS 2 Jazzy.
