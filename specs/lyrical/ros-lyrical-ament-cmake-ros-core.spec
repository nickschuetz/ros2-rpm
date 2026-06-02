%global ros_distro       lyrical
%global pkg_name         ament_cmake_ros_core
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-ament-cmake-ros-core
Version:        0.15.8
Release:        1%{?dist}
Summary:        ROS 2 Lyrical ament_cmake_ros_core

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/ament_cmake_ros-release
Source0:        https://github.com/ros2-gbp/ament_cmake_ros-release/archive/refs/tags/release/lyrical/ament_cmake_ros_core/0.15.8-1.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-lyrical-ament-cmake-core
BuildRequires:  ros-lyrical-ament-cmake-export-dependencies
BuildRequires:  ros-lyrical-ament-cmake-export-targets

Requires:       ros-lyrical-ament-cmake-core
Requires:       ros-lyrical-ament-cmake-libraries

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Core ROS specific CMake bits in the ament build system.

%prep
%autosetup -p1 -n ament_cmake_ros-release-release-lyrical-ament_cmake_ros_core-0.15.8-1

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
# CMake-macro package: ships only share/ cmake config + ament index sentinels,
# no compiled library (the generator's speculative .so line is dropped).
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/share/ament_index/resource_index/*/%{pkg_name}


%changelog
* Tue Jun 02 2026 Nick Schuetz <nschuetz@redhat.com> - 0.15.8-1
- Initial Fedora COPR build for ROS 2 Lyrical.
