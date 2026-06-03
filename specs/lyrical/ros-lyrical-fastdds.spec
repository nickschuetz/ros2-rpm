%global ros_distro       lyrical
%global pkg_name         fastdds
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-fastdds
Version:        3.6.1
Release:        1%{?dist}
Summary:        ROS 2 Lyrical fastdds

License:        Apache-2.0
URL:            https://www.eprosima.com/
Source0:        https://github.com/ros2-gbp/fastdds-release/archive/refs/tags/release/lyrical/fastdds/3.6.1-3.tar.gz#/%{pkg_name}-%{version}.tar.gz
Patch0:         fastdds/0001-disable-werror.patch


BuildRequires:  asio-devel
BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  python3-devel
BuildRequires:  ros-lyrical-fastcdr
BuildRequires:  ros-lyrical-foonathan-memory-vendor
BuildRequires:  tinyxml2-devel

Requires:       openssl-devel
Requires:       python3-devel
Requires:       ros-lyrical-fastcdr
Requires:       ros-lyrical-foonathan-memory-vendor
Requires:       tinyxml2-devel

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
eProsima Fast DDS is a C++ implementation of the DDS (Data Distribution
Service) standard of the OMG (Object Management Group). eProsima Fast DDS
implements the RTPS (Real Time Publish Subscribe) protocol, which provides
publisher-subscriber communications over unreliable transports such as UDP,
as defined and maintained by the Object Management Group (OMG) consortium.
RTPS is also the wire interoperability protocol defined for the Data
Distribution Service (DDS) standard. eProsima Fast DDS expose an API to
access directly the RTPS protocol, giving the user full access to the
protocol internals.

%prep
%autosetup -p1 -n fastdds-release-release-lyrical-fastdds-3.6.1-3

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
    -DSETUPTOOLS_DEB_LAYOUT=OFF -DBUILD_TESTING=OFF \
    -DCMAKE_COMPILE_WARNING_AS_ERROR=OFF
%cmake_build


%install
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
%cmake_install


%check
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
echo 'tests skipped (see CLAUDE.md / packages.yaml)'

%files
%license LICENSE
# Fast DDS ships the library, headers, CMake config (under share/), the
# discovery-server tools (bin/), and a tools/ data dir.
%{install_prefix}/bin/fastdds
%{install_prefix}/bin/fast-discovery-server
%{install_prefix}/bin/fast-discovery-server-1.0.1
%{install_prefix}/bin/ros-discovery
%{install_prefix}/include/%{pkg_name}/
%{install_prefix}/lib/lib%{pkg_name}.so*
%{install_prefix}/share/%{pkg_name}/
%{install_prefix}/tools/%{pkg_name}/


%changelog
* Tue Jun 02 2026 Nick Schuetz <nschuetz@redhat.com> - 3.6.1-1
- Initial Fedora COPR build for ROS 2 Lyrical.
