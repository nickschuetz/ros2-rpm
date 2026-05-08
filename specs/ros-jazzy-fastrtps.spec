%global ros_distro       jazzy
%global pkg_name         fastrtps
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-fastrtps
Version:        2.14.6
Release:        1%{?dist}
Summary:        ROS 2 Jazzy fastrtps

License:        Apache-2.0
URL:            https://www.eprosima.com/
Source0:        https://github.com/ros2-gbp/fastrtps-release/archive/refs/tags/release/jazzy/fastrtps/2.14.6-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  asio-devel
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  python3-devel
BuildRequires:  ros-jazzy-fastcdr
BuildRequires:  ros-jazzy-foonathan-memory-vendor
BuildRequires:  tinyxml2-devel

Requires:       openssl-devel
Requires:       python3-devel
Requires:       ros-jazzy-fastcdr
Requires:       ros-jazzy-foonathan-memory-vendor
Requires:       tinyxml2-devel

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
*eprosima Fast DDS* (formerly Fast RTPS) is a C++ implementation of the DDS
(Data Distribution Service) standard of the OMG (Object Management Group).
eProsima Fast DDS implements the RTPS (Real Time Publish Subscribe)
protocol, which provides publisher-subscriber communications over
unreliable transports such as UDP, as defined and maintained by the Object
Management Group (OMG) consortium. RTPS is also the wire interoperability
protocol defined for the Data Distribution Service (DDS) standard.
*eProsima Fast DDS* expose an API to access directly the RTPS protocol,
giving the user full access to the protocol internals.

%prep
%autosetup -p1 -n fastdds-release-release-jazzy-fastrtps-2.14.6-1

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
echo 'tests skipped — see CLAUDE.md / packages.yaml'

%files
%license LICENSE
# fastrtps: full eProsima Fast-DDS install. Headers, libs, schemas, and
# Python admin tools all under /opt/ros/jazzy/.
%{install_prefix}/include/fastrtps/
%{install_prefix}/include/fastdds/
%{install_prefix}/lib/libfastrtps.so*
%{install_prefix}/share/fastrtps/
%{install_prefix}/share/fastRTPS_profiles.xsd
%{install_prefix}/share/fastdds_static_discovery.xsd
%{install_prefix}/tools/
%{install_prefix}/bin/fastdds
%{install_prefix}/bin/fast-discovery-server*
%{install_prefix}/bin/ros-discovery


%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 2.14.6-1
- Initial Fedora COPR build for ROS 2 Jazzy.
