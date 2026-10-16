%global ros_distro       lyrical
%global pkg_name         simulation_interfaces
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-simulation-interfaces
Version:        2.1.0
Release:        1%{?dist}
Summary:        ROS 2 Lyrical simulation_interfaces

License:        Apache-2.0
URL:            https://github.com/ros-simulation/simulation-interfaces
Source0:        https://github.com/ros2-gbp/simulation_interfaces-release/archive/refs/tags/release/lyrical/simulation_interfaces/2.1.0-3.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-lyrical-action-msgs
BuildRequires:  ros-lyrical-ament-cmake
BuildRequires:  ros-lyrical-builtin-interfaces
BuildRequires:  ros-lyrical-geometry-msgs
BuildRequires:  ros-lyrical-rosidl-default-generators
BuildRequires:  ros-lyrical-std-msgs

Requires:       ros-lyrical-action-msgs
Requires:       ros-lyrical-builtin-interfaces
Requires:       ros-lyrical-geometry-msgs
Requires:       ros-lyrical-rosidl-default-runtime
Requires:       ros-lyrical-std-msgs

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Simulator-agnostic ROS 2 interfaces (messages, services and actions) for
controlling and querying a simulation: spawning and deleting entities,
stepping and resetting, and reading entity and world state. Used by the
O3DE SimulationInterfaces Gem.

%prep
%autosetup -p1 -n simulation_interfaces-release-release-lyrical-simulation_interfaces-2.1.0-3

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
%{install_prefix}/share/%{pkg_name}/
# Sentinels: ament_index/resource_index/<index>/<pkg>. Glob covers
# packages/, package_run_dependencies/, parent_prefix_path/, and any
# member_of_group entries (rosidl_runtime_packages, etc.).
%{install_prefix}/share/ament_index/resource_index/*/%{pkg_name}
# Message package: multiple typesupport .so variants + Python bindings.
%{install_prefix}/include/%{pkg_name}/
%{install_prefix}/lib/lib%{pkg_name}__rosidl_*.so
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}-py%{python3_version}.egg-info/


%changelog
* Fri Oct 16 2026 Nick Schuetz <nschuetz@redhat.com> - 2.1.0-1
- Initial Fedora COPR build for ROS 2 Lyrical.
