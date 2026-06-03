%global ros_distro       lyrical
%global pkg_name         rviz_ogre_vendor
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif
%global debug_package %{nil}

Name:           ros-%{ros_distro}-rviz-ogre-vendor
Version:        15.2.3
Release:        1%{?dist}
Summary:        ROS 2 Lyrical rviz_ogre_vendor

License:        Apache-2.0
URL:            https://www.ogre3d.org/
Source0:        https://github.com/ros2-gbp/rviz-release/archive/refs/tags/release/lyrical/rviz_ogre_vendor/15.2.3-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  freetype-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  libX11-devel
BuildRequires:  libXaw-devel
BuildRequires:  libXrandr-devel
BuildRequires:  mesa-libGL-devel mesa-libGLU-devel
BuildRequires:  python3-devel
BuildRequires:  ros-lyrical-ament-cmake
BuildRequires:  ros-lyrical-ament-cmake-vendor-package

Requires:       freetype
Requires:       freetype-devel
Requires:       glew-devel
Requires:       libX11-devel
Requires:       libXaw-devel
Requires:       libXrandr-devel
Requires:       mesa-libGL-devel mesa-libGLU-devel

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Wrapper around ogre3d, it provides a fixed CMake module and an
ExternalProject build of ogre.

%prep
%autosetup -p1 -n rviz-release-release-lyrical-rviz_ogre_vendor-15.2.3-1

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
# rviz_ogre_vendor builds a bundled Ogre and installs it under a package-owned
# opt/ subtree of the prefix; claim the whole tree (libs, plugins, headers, data).
%{install_prefix}/opt/rviz_ogre_vendor/


%changelog
* Wed Jun 03 2026 Nick Schuetz <nschuetz@redhat.com> - 15.2.3-1
- Initial Fedora COPR build for ROS 2 Lyrical.
