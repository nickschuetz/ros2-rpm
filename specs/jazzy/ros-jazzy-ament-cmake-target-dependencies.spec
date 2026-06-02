%global ros_distro       jazzy
%global pkg_name         ament_cmake_target_dependencies
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-ament-cmake-target-dependencies
Version:        2.5.6
Release:        1%{?dist}
Summary:        ROS 2 Jazzy ament_cmake_target_dependencies

License:        Apache-2.0
URL:            https://github.com/ament/ament_cmake
Source0:        https://github.com/ament/ament_cmake/archive/refs/tags/2.5.6.tar.gz#/ament_cmake-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake-core

Requires:       ros-jazzy-ament-cmake-core
Requires:       ros-jazzy-ament-cmake-include-directories
Requires:       ros-jazzy-ament-cmake-libraries

# Under /opt these libraries must not be exposed to the system dependency
# solver; under FHS (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
The ability to add definitions, include directories and libraries of a
package to a target in the ament build system in CMake.

%prep
%autosetup -p1 -n ament_cmake-2.5.6

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd ament_cmake_target_dependencies
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
    -DAMENT_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_PREFIX_PATH=%{install_prefix} \
    -DSETUPTOOLS_DEB_LAYOUT=OFF
%cmake_build
popd


%install
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd ament_cmake_target_dependencies
%cmake_install
popd


%check
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd ament_cmake_target_dependencies
%ctest
popd


%files
%license LICENSE
%doc ament_cmake_target_dependencies/CHANGELOG.rst
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/ament_index/resource_index/package_run_dependencies/%{pkg_name}
%{install_prefix}/share/ament_index/resource_index/parent_prefix_path/%{pkg_name}


%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 2.5.6-1
- Initial Fedora COPR build for ROS 2 Jazzy.
