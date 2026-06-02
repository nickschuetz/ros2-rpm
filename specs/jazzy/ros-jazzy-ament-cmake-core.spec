%global ros_distro       jazzy
%global pkg_name         ament_cmake_core
%global install_prefix   /opt/ros/%{ros_distro}

Name:           ros-%{ros_distro}-ament-cmake-core
Version:        2.5.6
Release:        1%{?dist}
Summary:        ROS 2 Jazzy ament_cmake_core: CMake macros for ament build system

License:        Apache-2.0
URL:            https://github.com/ament/ament_cmake
Source0:        https://github.com/ament/ament_cmake/archive/refs/tags/%{version}.tar.gz#/ament_cmake-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  python3-devel
BuildRequires:  python3-catkin_pkg
BuildRequires:  ros-jazzy-ament-package

Requires:       cmake
Requires:       python3-catkin_pkg
Requires:       ros-jazzy-ament-package

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
The core of the ament build system in CMake. Provides CMake macros and
support files for prefix-level setup, environment hooks, package indexing,
package templates, and install-via-symbolic-link support.

%prep
%autosetup -p1 -n ament_cmake-%{version}

%build
# ament_package is installed under %{install_prefix}, not the system Python
# path; CMake macros invoke Python and need to find it.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd %{pkg_name}
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
    -DAMENT_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_PREFIX_PATH=%{install_prefix} \
    -DSETUPTOOLS_DEB_LAYOUT=OFF
%cmake_build
popd

%install
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd %{pkg_name}
%cmake_install
popd

%check
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd %{pkg_name}
%ctest
popd

%files
%license LICENSE
%doc %{pkg_name}/CHANGELOG.rst
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/ament_index/resource_index/package_run_dependencies/%{pkg_name}
%{install_prefix}/share/ament_index/resource_index/parent_prefix_path/%{pkg_name}

%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 2.5.6-1
- Initial Fedora COPR build for ROS 2 Jazzy.
