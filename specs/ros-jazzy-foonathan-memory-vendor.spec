%global ros_distro       jazzy
%global pkg_name         foonathan_memory_vendor
%global install_prefix   /opt/ros/jazzy

# ExternalProject-based vendor: the C++ source is downloaded and built in a
# subdirectory that's outside RPM's awareness, so find-debuginfo's source
# scan finds nothing and debugsource ends up empty. Disable debug subpackages.
%global debug_package %{nil}

Name:           ros-%{ros_distro}-foonathan-memory-vendor
Version:        1.3.1
Release:        2%{?dist}
Summary:        ROS 2 Jazzy foonathan_memory_vendor

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/foonathan_memory_vendor-release
Source0:        https://github.com/ros2-gbp/foonathan_memory_vendor-release/archive/refs/tags/release/jazzy/foonathan_memory_vendor/1.3.1-3.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  python3-devel

Requires:       cmake

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Foonathan/memory vendor package for Fast-RTPS.

%prep
%autosetup -p1 -n foonathan_memory_vendor-release-release-jazzy-foonathan_memory_vendor-1.3.1-3
# Force the inner ExternalProject (the actual foonathan/memory upstream) to
# install into lib/ rather than the GNUInstallDirs default of lib64/. The
# outer wrapper's `install(DIRECTORY foo_mem_ext_prj_install/ ...)` copies
# the staged tree as-is, so the inner CMAKE_INSTALL_LIBDIR controls where
# libfoonathan_memory-*.so ends up in the final RPM.
sed -i 's|^    -DCMAKE_INSTALL_PREFIX=|    -DCMAKE_INSTALL_LIBDIR=lib\n    -DCMAKE_INSTALL_PREFIX=|' CMakeLists.txt

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
%cmake \
    -DCMAKE_INSTALL_PREFIX=%{install_prefix} \
    -DAMENT_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_PREFIX_PATH=%{install_prefix} \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DSETUPTOOLS_DEB_LAYOUT=OFF -DBUILD_TESTING=OFF
%cmake_build


%install
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
%cmake_install


%check
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
echo 'tests skipped — see CLAUDE.md / packages.yaml'

%files
%license LICENSE
%doc CHANGELOG.rst
# Vendor package: bundles the upstream foonathan_memory build under
# /opt/ros/jazzy/. Files land in lib64/ (Fedora's multi-arch path).
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/share/foonathan_memory/
%{install_prefix}/include/foonathan_memory/
%{install_prefix}/lib64/foonathan_memory/
%{install_prefix}/lib64/libfoonathan_memory-*.so*
%{install_prefix}/bin/nodesize_dbg


%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 1.3.1-1
- Initial Fedora COPR build for ROS 2 Jazzy.
