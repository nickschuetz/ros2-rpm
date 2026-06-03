%global ros_distro       lyrical
%global pkg_name         rosidl_generator_py
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-rosidl-generator-py
Version:        0.27.2
Release:        1%{?dist}
Summary:        ROS 2 Lyrical rosidl_generator_py

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/rosidl_python-release
Source0:        https://github.com/ros2-gbp/rosidl_python-release/archive/refs/tags/release/lyrical/rosidl_generator_py/0.27.2-3.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-lyrical-ament-cmake
BuildRequires:  ros-lyrical-rosidl-runtime-c

Requires:       python3-numpy
Requires:       python3-typing-extensions
Requires:       ros-lyrical-ament-cmake
Requires:       ros-lyrical-ament-index-python
Requires:       ros-lyrical-rmw
Requires:       ros-lyrical-rosidl-cli
Requires:       ros-lyrical-rosidl-generator-c
Requires:       ros-lyrical-rosidl-parser
Requires:       ros-lyrical-rosidl-pycommon
Requires:       ros-lyrical-rosidl-runtime-c
Requires:       ros-lyrical-rosidl-typesupport-c
Requires:       ros-lyrical-rosidl-typesupport-interface
Requires:       ros-lyrical-rpyutils

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Generate the ROS interfaces in Python.

%prep
%autosetup -p1 -n rosidl_python-release-release-lyrical-rosidl_generator_py-0.27.2-3

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
# (no LICENSE file in source tree; see package.xml <license>)
%doc CHANGELOG.rst
# TODO: review the file list against the build's "Installing:" log lines; the
# generator emits the conventional ament_cmake set but specific packages may
# need additions or trimming.
%{install_prefix}/share/%{pkg_name}/
# Sentinels: ament_index/resource_index/<index>/<pkg>. Glob covers
# packages/, package_run_dependencies/, parent_prefix_path/, and any
# member_of_group entries (rosidl_runtime_packages, etc.).
%{install_prefix}/share/ament_index/resource_index/*/%{pkg_name}
# Python generator package: Python module + egg-info + the lib/<pkg>/ codegen
# templates. No top-level include/ or typesupport .so of its own (those are
# produced per message package that uses this generator).
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}-py%{python3_version}.egg-info/
%{install_prefix}/lib/%{pkg_name}/


%changelog
* Tue Jun 02 2026 Nick Schuetz <nschuetz@redhat.com> - 0.27.2-1
- Initial Fedora COPR build for ROS 2 Lyrical.
