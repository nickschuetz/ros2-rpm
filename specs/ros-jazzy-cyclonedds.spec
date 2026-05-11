%global ros_distro       jazzy
%global pkg_name         cyclonedds
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-cyclonedds
Version:        0.10.5
Release:        1%{?dist}
Summary:        ROS 2 Jazzy cyclonedds

License:        EPL-2.0
URL:            https://projects.eclipse.org/projects/iot.cyclonedds
Source0:        https://github.com/ros2-gbp/cyclonedds-release/archive/refs/tags/release/jazzy/cyclonedds/0.10.5-1.tar.gz#/%{pkg_name}-%{version}.tar.gz


BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  python3-devel

Requires:       openssl

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Eclipse Cyclone DDS is a very performant and robust open-source DDS
implementation. Cyclone DDS is developed completely in the open as an
Eclipse IoT project.

%prep
%autosetup -p1 -n cyclonedds-release-release-jazzy-cyclonedds-0.10.5-1

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
    -DENABLE_SHM=OFF \
    -DENABLE_SECURITY=ON
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
# Cyclone DDS is upstream Eclipse, not a bloom-shaped ROS package. The
# %files list below was derived from a local mock build's "-- Installing:"
# log, list explicitly rather than glob to keep ownership scoped to this
# package only.
%{install_prefix}/include/dds/
%{install_prefix}/include/ddsc/
%{install_prefix}/include/idl/
%{install_prefix}/include/idlc/
%{install_prefix}/lib/libddsc.so*
%{install_prefix}/lib/libcycloneddsidl.so*
%{install_prefix}/lib/libdds_security_ac.so
%{install_prefix}/lib/libdds_security_auth.so
%{install_prefix}/lib/libdds_security_crypto.so
%{install_prefix}/lib/cmake/CycloneDDS/
%{install_prefix}/lib/pkgconfig/CycloneDDS.pc
%{install_prefix}/bin/idlc
%{install_prefix}/bin/ddsperf
%doc %{install_prefix}/share/doc


%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 0.10.5-1
- Initial Fedora COPR build for ROS 2 Jazzy.
