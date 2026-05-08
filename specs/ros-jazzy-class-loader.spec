%global ros_distro       jazzy
%global pkg_name         class_loader
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-class-loader
Version:        2.7.0
Release:        1%{?dist}
Summary:        ROS 2 Jazzy class_loader

License:        BSD-3-Clause
URL:            http://ros.org/wiki/class_loader
Source0:        https://github.com/ros2-gbp/class_loader-release/archive/refs/tags/release/jazzy/class_loader/2.7.0-3.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  console-bridge-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake
BuildRequires:  ros-jazzy-ament-cmake-ros
BuildRequires:  ros-jazzy-console-bridge-vendor
BuildRequires:  ros-jazzy-rcpputils

Requires:       console-bridge-devel
Requires:       ros-jazzy-console-bridge-vendor
Requires:       ros-jazzy-rcpputils

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
The class_loader package is a ROS-independent package for loading plugins
during runtime and the foundation of the higher level ROS "pluginlib"
library. class_loader utilizes the host operating system's runtime loader
to open runtime libraries (e.g. .so/.dll files), introspect the library for
exported plugin classes, and allows users to instantiate objects of these
exported classes without the explicit declaration (i.e. header file) for
those classes.

%prep
%autosetup -p1 -n class_loader-release-release-jazzy-class_loader-2.7.0-3

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
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 2.7.0-1
- Initial Fedora COPR build for ROS 2 Jazzy.
