%global ros_distro       jazzy
%global pkg_name         rosidl_generator_py
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rosidl-generator-py
Version:        0.22.2
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rosidl_generator_py

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/rosidl_python-release
Source0:        https://github.com/ros2-gbp/rosidl_python-release/archive/refs/tags/release/jazzy/rosidl_generator_py/0.22.2-1.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake
BuildRequires:  ros-jazzy-rosidl-runtime-c

Requires:       python3-numpy
Requires:       ros-jazzy-ament-cmake
Requires:       ros-jazzy-ament-index-python
Requires:       ros-jazzy-rosidl-cli
Requires:       ros-jazzy-rosidl-generator-c
Requires:       ros-jazzy-rosidl-parser
Requires:       ros-jazzy-rosidl-pycommon
Requires:       ros-jazzy-rosidl-runtime-c
Requires:       ros-jazzy-rosidl-typesupport-c
Requires:       ros-jazzy-rosidl-typesupport-interface

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Generate the ROS interfaces in Python.

%prep
%autosetup -p1 -n rosidl_python-release-release-jazzy-rosidl_generator_py-0.22.2-1

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
# (no LICENSE file in source tree — see package.xml <license>)
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
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}-py%{python3_version}.egg-info/
%{install_prefix}/lib/%{pkg_name}/


%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 0.22.2-1
- Initial Fedora COPR build for ROS 2 Jazzy.
