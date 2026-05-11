%global ros_distro       jazzy
%global pkg_name         fastcdr
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-fastcdr
Version:        2.2.7
Release:        1%{?dist}
Summary:        ROS 2 Jazzy fastcdr

License:        Apache-2.0
URL:            https://www.eprosima.com/
Source0:        https://github.com/ros2-gbp/fastcdr-release/archive/refs/tags/release/jazzy/fastcdr/2.2.7-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel



%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
*eProsima Fast CDR* is a C++ serialization library implementing the Common
Data Representation (CDR) mechanism defined by the Object Management Group
(OMG) consortium. CDR is the serialization mechanism used in DDS for the
DDS Interoperability Wire Protocol (DDSI-RTPS).

%prep
%autosetup -p1 -n fastcdr-release-release-jazzy-fastcdr-2.2.7-1

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
# Header install lives in src/cpp/CMakeLists.txt so the generator's root-only
# detection missed it; enumerate explicitly here.
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/include/%{pkg_name}/
%{install_prefix}/lib/lib%{pkg_name}.so*
%{install_prefix}/lib/cmake/%{pkg_name}/


%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 2.2.7-1
- Initial Fedora COPR build for ROS 2 Jazzy.
