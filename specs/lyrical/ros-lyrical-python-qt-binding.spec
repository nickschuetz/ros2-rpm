%global ros_distro       lyrical
%global pkg_name         python_qt_binding
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif
%global debug_package %{nil}

Name:           ros-%{ros_distro}-python-qt-binding
Version:        2.5.4
Release:        1%{?dist}
Summary:        ROS 2 Lyrical python_qt_binding

License:        BSD-3-Clause
URL:            http://ros.org/wiki/python_qt_binding
Source0:        https://github.com/ros2-gbp/python_qt_binding-release/archive/refs/tags/release/lyrical/python_qt_binding/2.5.4-3.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  python3-pyqt6-devel python3-pyqt6-sip sip6 PyQt-builder
BuildRequires:  ros-lyrical-ament-cmake

Requires:       python3-devel
Requires:       python3-pyqt6-devel python3-pyqt6-sip sip6 PyQt-builder

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
This stack provides Python bindings for Qt. There are two providers: pyside
and pyqt. PySide2 is available under the GPL, LGPL and a commercial
license. PyQt is released under the GPL.

Both the bindings and tools to build bindings are included from each
available provider. For PySide, it is called "Shiboken". For PyQt, this is
called "SIP".

Also provided is adapter code to make the user's Python code independent of
which binding provider was actually used which makes it very easy to switch
between these.

%prep
%autosetup -p1 -n python_qt_binding-release-release-lyrical-python_qt_binding-2.5.4-3

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
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}-py%{python3_version}.egg-info/


%changelog
* Wed Jun 03 2026 Nick Schuetz <nschuetz@redhat.com> - 2.5.4-1
- Initial Fedora COPR build for ROS 2 Lyrical.
