%global ros_distro       jazzy
%global pkg_name         tracetools
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-tracetools
Version:        8.2.5
Release:        1%{?dist}
Summary:        ROS 2 Jazzy tracetools

License:        Apache-2.0
URL:            https://docs.ros.org/en/rolling/p/tracetools/
Source0:        https://github.com/ros2-gbp/ros2_tracing-release/archive/refs/tags/release/jazzy/tracetools/8.2.5-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  lttng-ust-devel
BuildRequires:  pkgconfig
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake-gen-version-h
BuildRequires:  ros-jazzy-ament-cmake-ros

Requires:       lttng-tools
Requires:       lttng-ust-devel

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Tracing wrapper for ROS 2.

%prep
%autosetup -p1 -n ros2_tracing-release-release-jazzy-tracetools-8.2.5-1

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
%{install_prefix}/lib/libtracetools_status.so*
%{install_prefix}/lib/%{pkg_name}/


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 8.2.5-1
- Initial Fedora COPR build for ROS 2 Jazzy.
