%global ros_distro       jazzy
%global pkg_name         ament_cmake_ros
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-ament-cmake-ros
Version:        0.12.0
Release:        1%{?dist}
Summary:        ROS 2 Jazzy ament_cmake_ros

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/ament_cmake_ros-release
Source0:        https://github.com/ros2-gbp/ament_cmake_ros-release/archive/refs/tags/release/jazzy/ament_cmake_ros/0.12.0-3.tar.gz#/ament_cmake_ros-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake

Requires:       ros-jazzy-ament-cmake
# ament_cmake_ros-extras.cmake unconditionally find_package()s these test
# framework packages; without these Requires every consumer's CMake configure
# fails. Upstream's package.xml omits them, workaround locally.
Requires:       ros-jazzy-ament-cmake-gmock
Requires:       ros-jazzy-ament-cmake-gtest
Requires:       ros-jazzy-ament-cmake-pytest

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
The ROS specific CMake bits in the ament build system.

%prep
%autosetup -p1 -n ament_cmake_ros-release-release-jazzy-ament_cmake_ros-0.12.0-3

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
    -DAMENT_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_PREFIX_PATH=%{install_prefix} \
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
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/ament_index/resource_index/package_run_dependencies/%{pkg_name}
%{install_prefix}/share/ament_index/resource_index/parent_prefix_path/%{pkg_name}


%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 0.12.0-1
- Initial Fedora COPR build for ROS 2 Jazzy.
