%global ros_distro       lyrical
%global pkg_name         urdfdom_headers
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-urdfdom-headers
Version:        3.0.0
Release:        1%{?dist}
Summary:        ROS 2 Lyrical urdfdom_headers

License:        BSD-3-Clause
URL:            http://ros.org/wiki/urdf
Source0:        https://github.com/ros2-gbp/urdfdom_headers-release/archive/refs/tags/release/lyrical/urdfdom_headers/3.0.0-3.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel



# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
C++ headers for URDF.

%prep
%autosetup -p1 -n urdfdom_headers-release-release-lyrical-urdfdom_headers-3.0.0-3

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
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
# Header-only (INTERFACE target, no compiled lib). Installs the urdf_* header
# trees directly under include/, plus a CMake package config and pkg-config.
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/include/urdf_exception/
%{install_prefix}/include/urdf_model/
%{install_prefix}/include/urdf_sensor/
%{install_prefix}/include/urdf_world/
%{install_prefix}/lib/%{pkg_name}/
%{install_prefix}/lib/pkgconfig/%{pkg_name}.pc


%changelog
* Thu Jun 04 2026 Nick Schuetz <nschuetz@redhat.com> - 3.0.0-1
- Initial Fedora COPR build for ROS 2 Lyrical.
