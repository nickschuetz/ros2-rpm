%global ros_distro       lyrical
%global pkg_name         urdfdom
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-urdfdom
Version:        6.0.0
Release:        1%{?dist}
Summary:        ROS 2 Lyrical urdfdom

License:        BSD-3-Clause
URL:            https://github.com/ros2-gbp/urdfdom-release
Source0:        https://github.com/ros2-gbp/urdfdom-release/archive/refs/tags/release/lyrical/urdfdom/6.0.0-3.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  console-bridge-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-lyrical-console-bridge-vendor
BuildRequires:  tinyxml2-devel

Requires:       console-bridge-devel
Requires:       ros-lyrical-console-bridge-vendor
Requires:       tinyxml2-devel

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
A library to access URDFs using the DOM model.

%prep
%autosetup -p1 -n urdfdom-release-release-lyrical-urdfdom-6.0.0-3

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
%doc CHANGELOG.rst
# Plain-CMake upstream (not ament): compiled parser libraries, urdf_parser
# headers, CMake package config, pkg-config, and the check_urdf / urdf_to_graphviz
# tools. The urdf_model headers come from the system urdfdom-headers-devel.
%{install_prefix}/lib/liburdfdom*.so*
%{install_prefix}/include/urdf_parser/
%{install_prefix}/lib/cmake/urdfdom/
%{install_prefix}/lib/pkgconfig/urdfdom.pc
%{install_prefix}/bin/*
%{install_prefix}/share/%{pkg_name}/


%changelog
* Thu Jun 04 2026 Nick Schuetz <nschuetz@redhat.com> - 6.0.0-1
- Initial Fedora COPR build for ROS 2 Lyrical.
