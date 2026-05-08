%global ros_distro       jazzy
%global pkg_name         rcutils
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rcutils
Version:        6.7.5
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rcutils

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/rcutils-release
Source0:        https://github.com/ros2-gbp/rcutils-release/archive/refs/tags/release/jazzy/rcutils/6.7.5-1.tar.gz#/rcutils-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  libatomic
BuildRequires:  python3-devel
BuildRequires:  python3-empy
BuildRequires:  ros-jazzy-ament-cmake-ros

Requires:       libatomic

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Package containing various utility types and functions for C

%prep
%autosetup -p1 -n rcutils-release-release-jazzy-rcutils-6.7.5-1

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
echo 'tests skipped — see CLAUDE.md / packages.yaml'

%files
%license LICENSE
%doc CHANGELOG.rst
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/ament_index/resource_index/package_run_dependencies/%{pkg_name}
%{install_prefix}/share/ament_index/resource_index/parent_prefix_path/%{pkg_name}
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}-py%{python3_version}.egg-info/
%{install_prefix}/include/%{pkg_name}/
%{install_prefix}/lib/lib%{pkg_name}.so*


%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 6.7.5-1
- Initial Fedora COPR build for ROS 2 Jazzy.
