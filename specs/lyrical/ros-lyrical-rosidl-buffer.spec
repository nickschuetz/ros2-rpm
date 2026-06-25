%global ros_distro       lyrical
%global pkg_name         rosidl_buffer
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-rosidl-buffer
Version:        5.2.1
Release:        1%{?dist}
Summary:        ROS 2 Lyrical rosidl_buffer

License:        Apache-2.0
URL:            https://github.com/ros2/rosidl
Source0:        https://github.com/ros2/rosidl/archive/refs/tags/5.2.1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-lyrical-ament-cmake



# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Core Buffer types and implementations for ROS2 native buffer feature.
Provides Buffer container type with support for multiple memory backends
(CPU, GPU, custom).

%prep
%autosetup -p1 -n rosidl-5.2.0

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
pushd rosidl_buffer > /dev/null
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
pushd rosidl_buffer > /dev/null
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
%{install_prefix}/include/%{pkg_name}/
%{install_prefix}/lib/lib%{pkg_name}.so*


%changelog
* Thu Jun 25 2026 Nick Schuetz <nschuetz@redhat.com> - 5.2.1-1
- Sync with upstream lyrical: 5.2.1.

* Tue Jun 02 2026 Nick Schuetz <nschuetz@redhat.com> - 5.2.0-1
- Initial Fedora COPR build for ROS 2 Lyrical.
