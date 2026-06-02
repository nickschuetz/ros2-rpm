%global ros_distro       jazzy
%global pkg_name         ament_cmake_vendor_package
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-ament-cmake-vendor-package
Version:        2.5.6
Release:        1%{?dist}
Summary:        ROS 2 Jazzy ament_cmake_vendor_package

License:        Apache-2.0
URL:            https://github.com/ament/ament_cmake
Source0:        https://github.com/ament/ament_cmake/archive/refs/tags/2.5.6.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake-core
BuildRequires:  ros-jazzy-ament-cmake-export-dependencies

Requires:       git
Requires:       python3-vcstool
Requires:       ros-jazzy-ament-cmake-core
Requires:       ros-jazzy-ament-cmake-export-dependencies

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Macros for maintaining a 'vendor' package.

%prep
%autosetup -p1 -n ament_cmake-2.5.6

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd ament_cmake_vendor_package > /dev/null
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
popd > /dev/null


%install
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd ament_cmake_vendor_package > /dev/null
%cmake_install
popd > /dev/null


%check
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
echo 'tests skipped (see CLAUDE.md / packages.yaml)'

%files
%license LICENSE
# (no CHANGELOG.rst in source tree)
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
%{install_prefix}/share/%{pkg_name}/
# Sentinels: ament_index/resource_index/<index>/<pkg>. Glob covers
# packages/, package_run_dependencies/, parent_prefix_path/, and any
# member_of_group entries (rosidl_runtime_packages, etc.).
%{install_prefix}/share/ament_index/resource_index/*/%{pkg_name}


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 2.5.6-1
- Initial Fedora COPR build for ROS 2 Jazzy.
