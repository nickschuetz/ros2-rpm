%global ros_distro       jazzy
%global pkg_name         tinyxml2_vendor
%global install_prefix   /opt/ros/jazzy
%global debug_package %{nil}

Name:           ros-%{ros_distro}-tinyxml2-vendor
Version:        0.9.2
Release:        1%{?dist}
Summary:        ROS 2 Jazzy tinyxml2_vendor

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/tinyxml2_vendor-release
Source0:        https://github.com/ros2-gbp/tinyxml2_vendor-release/archive/refs/tags/release/jazzy/tinyxml2_vendor/0.9.2-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake
BuildRequires:  tinyxml2-devel

Requires:       tinyxml2-devel

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Wrapper around tinyxml2, providing nothing but a dependency on tinyxml2, on
some systems. On others, it provides a fixed CMake module or even an
ExternalProject build of tinyxml2.

%prep
%autosetup -p1 -n tinyxml2_vendor-release-release-jazzy-tinyxml2_vendor-0.9.2-1

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
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 0.9.2-1
- Initial Fedora COPR build for ROS 2 Jazzy.
