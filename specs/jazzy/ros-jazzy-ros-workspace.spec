%global ros_distro       jazzy
%global pkg_name         ros_workspace
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-ros-workspace
Version:        1.0.3
Release:        1%{?dist}
Summary:        ROS 2 Jazzy ros_workspace

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/ros_workspace-release
Source0:        https://github.com/ros2-gbp/ros_workspace-release/archive/refs/tags/release/jazzy/ros_workspace/1.0.3-7.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-ament-cmake-core
BuildRequires:  ros-jazzy-ament-package



%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Provides the prefix level environment files for ROS 2 packages.

%prep
%autosetup -p1 -n ros_workspace-release-release-jazzy-ros_workspace-1.0.3-7

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
%{install_prefix}/share/ament_index/resource_index/*/%{pkg_name}
# ros_workspace generates the canonical workspace setup files at the
# install prefix root (this is the package that makes
# `source /opt/ros/jazzy/setup.bash` work).
%{install_prefix}/setup.bash
%{install_prefix}/setup.sh
%{install_prefix}/setup.zsh
%{install_prefix}/local_setup.bash
%{install_prefix}/local_setup.sh
%{install_prefix}/local_setup.zsh
%{install_prefix}/_local_setup_util.py


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 1.0.3-1
- Initial Fedora COPR build for ROS 2 Jazzy.
