%global ros_distro       jazzy
%global pkg_name         builtin_interfaces
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-builtin-interfaces
Version:        2.0.3
Release:        1%{?dist}
Summary:        ROS 2 Jazzy builtin_interfaces

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/rcl_interfaces-release
Source0:        https://github.com/ros2-gbp/rcl_interfaces-release/archive/refs/tags/release/jazzy/builtin_interfaces/2.0.3-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake
BuildRequires:  ros-jazzy-rosidl-core-generators
# rosidl_generator_py's CMake macros find_package(python_cmake_module) at
# generate-interfaces time — pull it in explicitly here.
BuildRequires:  ros-jazzy-python-cmake-module
# rosidl_generator_py imports rpyutils at code-gen time.
BuildRequires:  ros-jazzy-rpyutils

Requires:       ros-jazzy-rosidl-core-runtime

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
A package containing message and service definitions for types defined in
the OMG IDL Platform Specific Model.

%prep
%autosetup -p1 -n rcl_interfaces-release-release-jazzy-builtin_interfaces-2.0.3-1

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
%doc CHANGELOG.rst
# Message package: ships generated headers, multiple per-typesupport .so
# libraries, Python bindings, and ament_index sentinels.
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/share/ament_index/resource_index/*/%{pkg_name}
%{install_prefix}/include/%{pkg_name}/
%{install_prefix}/lib/lib%{pkg_name}__rosidl_*.so
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}-py%{python3_version}.egg-info/


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 2.0.3-1
- Initial Fedora COPR build for ROS 2 Jazzy.
