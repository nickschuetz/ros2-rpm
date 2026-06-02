%global ros_distro       jazzy
%global pkg_name         rosidl_parser
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rosidl-parser
Version:        4.6.7
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rosidl_parser

License:        Apache-2.0
URL:            https://github.com/ros2/rosidl
Source0:        https://github.com/ros2/rosidl/archive/refs/tags/4.6.7.tar.gz#/rosidl-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake

Requires:       python3-lark-parser
Requires:       ros-jazzy-rosidl-adapter

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
The parser for `.idl` ROS interface files.

%prep
%autosetup -p1 -n rosidl-4.6.7

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd rosidl_parser > /dev/null
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
    -DAMENT_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_PREFIX_PATH=%{install_prefix} \
    -DSETUPTOOLS_DEB_LAYOUT=OFF -DBUILD_TESTING=OFF
%cmake_build
popd > /dev/null


%install
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd rosidl_parser > /dev/null
%cmake_install
popd > /dev/null


%check
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
echo 'tests skipped (see CLAUDE.md / packages.yaml)'

%files
%license LICENSE
%doc rosidl_parser/CHANGELOG.rst
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
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 4.6.7-1
- Initial Fedora COPR build for ROS 2 Jazzy.
