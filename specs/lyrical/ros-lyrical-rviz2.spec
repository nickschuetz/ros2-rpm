%global ros_distro       lyrical
%global pkg_name         rviz2
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-rviz2
Version:        15.2.3
Release:        1%{?dist}
Summary:        ROS 2 Lyrical rviz2

License:        BSD-3-Clause
URL:            https://github.com/ros2/rviz/blob/ros2/README.md
Source0:        https://github.com/ros2-gbp/rviz-release/archive/refs/tags/release/lyrical/rviz2/15.2.3-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  chrpath
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  ros-lyrical-ament-cmake
BuildRequires:  ros-lyrical-rviz-common
BuildRequires:  ros-lyrical-rviz-default-plugins
BuildRequires:  ros-lyrical-rviz-ogre-vendor
# find_package(rviz_common) and find_package(rviz_default_plugins) re-run
# find_package for every one of their exported dependencies, so the full
# transitive closure must be present in this buildroot.
BuildRequires:  ros-lyrical-eigen3-cmake-module
BuildRequires:  ros-lyrical-geometry-msgs
BuildRequires:  ros-lyrical-gz-math-vendor
BuildRequires:  ros-lyrical-image-transport
BuildRequires:  ros-lyrical-interactive-markers
BuildRequires:  ros-lyrical-laser-geometry
BuildRequires:  ros-lyrical-map-msgs
BuildRequires:  ros-lyrical-message-filters
BuildRequires:  ros-lyrical-nav-msgs
BuildRequires:  ros-lyrical-pluginlib
BuildRequires:  ros-lyrical-point-cloud-transport
BuildRequires:  ros-lyrical-rclcpp
BuildRequires:  ros-lyrical-resource-retriever
BuildRequires:  ros-lyrical-resource-retriever-service-plugin
BuildRequires:  ros-lyrical-rviz-rendering
BuildRequires:  ros-lyrical-sensor-msgs
BuildRequires:  ros-lyrical-std-msgs
BuildRequires:  ros-lyrical-std-srvs
BuildRequires:  ros-lyrical-tf2
BuildRequires:  ros-lyrical-tf2-geometry-msgs
BuildRequires:  ros-lyrical-tf2-ros
BuildRequires:  ros-lyrical-urdf
BuildRequires:  ros-lyrical-urdfdom
BuildRequires:  ros-lyrical-urdfdom-headers
BuildRequires:  ros-lyrical-visualization-msgs
BuildRequires:  ros-lyrical-yaml-cpp-vendor

Requires:       python3-devel
Requires:       ros-lyrical-rviz-common
Requires:       ros-lyrical-rviz-default-plugins
Requires:       ros-lyrical-rviz-ogre-vendor

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
3D visualization tool for ROS.

%prep
%autosetup -p1 -n rviz-release-release-lyrical-rviz2-15.2.3-1

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
# The gz vendor packages (pulled transitively via rviz_default_plugins ->
# gz_math_vendor) stage their inner libs under opt/<vendor>/ and rely on sourced
# ament environment hooks that do not fire under rpmbuild; add the opt paths so
# find_package(gz_math_vendor) and its gz-utils/gz-cmake chain resolve.
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
    -DAMENT_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_PREFIX_PATH="%{install_prefix};%{install_prefix}/opt/gz_cmake_vendor;%{install_prefix}/opt/gz_utils_vendor;%{install_prefix}/opt/gz_math_vendor" \
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

# rviz2 installs only the rviz2 executable (no libraries land in
# %{install_prefix}/lib), so its baked-in RPATH points at directories that are
# absent from this package's own buildroot and check-rpaths rejects them
# (error 0002). The libraries (rviz_common, rviz_rendering, Ogre) are resolved
# at runtime from %{install_prefix}/lib and the ogre vendor opt dir via the
# setup.bash LD_LIBRARY_PATH hooks, so the RPATH is redundant; strip it. This
# also guarantees no build-tree path can leak through an RPATH.
for f in %{buildroot}%{install_prefix}/bin/rviz2 \
         %{buildroot}%{install_prefix}/lib/%{pkg_name}/rviz2; do
    chrpath --delete "$f" || :
done


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
# rviz2 ships the rviz2 launcher executable (bin/ plus the ament-private copy
# under lib/rviz2/ alongside rviz1_to_rviz2.py); it installs no libraries.
%{install_prefix}/bin/%{pkg_name}
%{install_prefix}/lib/%{pkg_name}/


%changelog
* Wed Jun 03 2026 Nick Schuetz <nschuetz@redhat.com> - 15.2.3-1
- Initial Fedora COPR build for ROS 2 Lyrical.
