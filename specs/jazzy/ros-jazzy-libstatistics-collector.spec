%global ros_distro       jazzy
%global pkg_name         libstatistics_collector
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-libstatistics-collector
Version:        1.7.4
Release:        1%{?dist}
Summary:        ROS 2 Jazzy libstatistics_collector

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/libstatistics_collector-release
Source0:        https://github.com/ros2-gbp/libstatistics_collector-release/archive/refs/tags/release/jazzy/libstatistics_collector/1.7.4-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake-ros
BuildRequires:  ros-jazzy-builtin-interfaces
BuildRequires:  ros-jazzy-rcl
BuildRequires:  ros-jazzy-rcpputils
BuildRequires:  ros-jazzy-rmw
BuildRequires:  ros-jazzy-statistics-msgs

Requires:       ros-jazzy-builtin-interfaces
Requires:       ros-jazzy-rcl
Requires:       ros-jazzy-rcpputils
Requires:       ros-jazzy-rmw
Requires:       ros-jazzy-statistics-msgs

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Lightweight aggregation utilities to collect statistics and measure message
metrics.

%prep
%autosetup -p1 -n libstatistics_collector-release-release-jazzy-libstatistics_collector-1.7.4-1

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
%license LICENSE
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
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 1.7.4-1
- Initial Fedora COPR build for ROS 2 Jazzy.
