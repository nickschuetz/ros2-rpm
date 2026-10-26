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
Version:        3.6.2
Release:        3%{?dist}
Summary:        ROS 2 Lyrical fastdds

License:        Apache-2.0
URL:            https://www.eprosima.com/
Source0:        https://github.com/ros2-gbp/fastdds-release/archive/refs/tags/release/lyrical/fastdds/3.6.2-1.tar.gz#/%{pkg_name}-%{version}.tar.gz
Patch0:         fastdds/0001-disable-werror.patch
# Security plugins vs. Fedora's OpenSSL: const X509_NAME getters in OpenSSL 4.0
# (Fedora 45, rawhide) and the always-taken pre-3.0 include branch that pulls in
# openssl/engine.h, which Fedora 44's no-engine OpenSSL 3.5 does not ship.
Patch1:         fastdds/0002-openssl4-const-x509-name.patch
Patch2:         fastdds/0003-opensslv-before-version-check.patch


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
%autosetup -p1 -n fastdds-release-release-lyrical-fastdds-3.6.2-1

%build
# Make our previously-installed ROS Python packages discoverable to CMake's
# execute_process invocations of python3.
export PYTHONPATH=%{install_prefix}/lib/python%{python3_version}/site-packages${PYTHONPATH:+:$PYTHONPATH}
# SECURITY=ON compiles the DDS Security plugins (DDS:Auth:PKI-DH,
# DDS:Access:Permissions, DDS:Crypto:AES-GCM-GMAC) into libfastdds, as the
# upstream ROS 2 binaries do, so SROS2 works on rmw_fastrtps_cpp. It also sets
# HAVE_SECURITY in the installed config.hpp, which changes public header
# layouts: every package that builds against Fast DDS must be rebuilt.
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
    -DCMAKE_COMPILE_WARNING_AS_ERROR=OFF \
    -DSECURITY=ON
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
* Mon Oct 26 2026 Nick Schuetz <nschuetz@redhat.com> - 3.6.2-3
- Carry 0002-openssl4-const-x509-name.patch (backport of upstream PR 6487):
  OpenSSL 4.0 on Fedora 45 and rawhide returns const X509_NAME* from
  X509_get_subject_name(), which the security plugins assigned to non-const.
- Carry 0003-opensslv-before-version-check.patch: Pkcs11Provider.hpp and
  FileProvider.hpp tested OPENSSL_VERSION_NUMBER before including any OpenSSL
  header, so they always included openssl/engine.h, absent from Fedora 44's
  no-engine OpenSSL 3.5. Both only bite with -DSECURITY=ON (3.6.2-2 failed
  on all six Fedora chroots; CentOS Stream 10 was fine).

* Mon Oct 26 2026 Nick Schuetz <nschuetz@redhat.com> - 3.6.2-2
- Build with -DSECURITY=ON so the DDS Security plugins are available and
  SROS2 (ROS_SECURITY_ENABLE=true) works on rmw_fastrtps_cpp, matching the
  upstream ROS 2 binaries. HAVE_SECURITY changes public header layouts, so
  the rmw_fastrtps packages and rosidl_dynamic_typesupport_fastrtps are
  rebuilt against this release.

* Mon Jul 27 2026 Nick Schuetz <nschuetz@redhat.com> - 3.6.2-1
- Sync with upstream lyrical: 3.6.2.

* Tue Jun 02 2026 Nick Schuetz <nschuetz@redhat.com> - 3.6.1-1
- Initial Fedora COPR build for ROS 2 Lyrical.
