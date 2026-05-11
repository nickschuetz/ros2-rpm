%global ros_distro       jazzy
%global pkg_name         rcpputils
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rcpputils
Version:        2.11.3
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rcpputils

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/rcpputils-release
Source0:        https://github.com/ros2-gbp/rcpputils-release/archive/refs/tags/release/jazzy/rcpputils/2.11.3-1.tar.gz#/rcpputils-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake
BuildRequires:  ros-jazzy-ament-cmake-gen-version-h
BuildRequires:  ros-jazzy-ament-cmake-ros
BuildRequires:  ros-jazzy-rcutils

Requires:       ros-jazzy-rcutils

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Package containing utility code for C++.

%prep
%autosetup -p1 -n rcpputils-release-release-jazzy-rcpputils-2.11.3-1

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
%license LICENSE
%doc CHANGELOG.rst
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
%{install_prefix}/share/%{pkg_name}/
# Sentinels: ament_index/resource_index/<index>/<pkg>. Standard ones include
# packages/, package_run_dependencies/, parent_prefix_path/, and any group the
# package is member_of (rosidl_runtime_packages, rosidl_interface_packages, etc.).
# A glob covers all of them in one line.
%{install_prefix}/share/ament_index/resource_index/*/%{pkg_name}
%{install_prefix}/include/%{pkg_name}/
%{install_prefix}/lib/lib%{pkg_name}.so*


%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 2.11.3-1
- Initial Fedora COPR build for ROS 2 Jazzy.
