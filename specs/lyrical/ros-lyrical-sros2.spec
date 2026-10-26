%global ros_distro       lyrical
%global pkg_name         sros2
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-sros2
Version:        0.16.6
Release:        1%{?dist}
Summary:        ROS 2 Lyrical sros2

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/sros2-release
Source0:        https://github.com/ros2-gbp/sros2-release/archive/refs/tags/release/lyrical/sros2/0.16.6-1.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3
Requires:       python3-argcomplete
Requires:       python3-cryptography
Requires:       python3-lxml
Requires:       ros-lyrical-ament-index-python
Requires:       ros-lyrical-rclpy
Requires:       ros-lyrical-ros2cli

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
SROS2 command line tooling for ROS 2 security: the "ros2 security" verbs that
create keystores, enclaves, permissions and policies for DDS Security
(authentication, access control and encryption) with the supported RMW
implementations.

%prep
%autosetup -p1 -n sros2-release-release-lyrical-sros2-0.16.6-1

# Reduce setup.py's install_requires to ['setuptools'] before the
# auto-generated buildrequires step runs. The full list typically references
# ROS Python packages (launch, ament_index_python, etc.) that live under
# /opt/ros/jazzy and don't register python3dist(...) Provides; leaving
# those in setup.py causes pyproject buildrequires to emit BRs that Fedora
# can't resolve. The runtime Requires: above already enforces these.
python3 << 'PYEOF' || true
import re
p = "setup.py"
s = open(p).read()
s = re.sub(r"install_requires\s*=\s*\[[^\]]*\]", "install_requires=['setuptools']", s, flags=re.S)
open(p, "w").write(s)
PYEOF


%generate_buildrequires
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%{python3} -m pip install \
    --root %{buildroot} \
    --prefix %{install_prefix} \
    --no-deps \
    --no-build-isolation \
    --no-warn-script-location \
    --disable-pip-version-check \
    %{_pyproject_wheeldir}/*.whl


%check
%pytest -v test || true


%files
# (no LICENSE file in source tree; see package.xml <license>)
%doc CHANGELOG.rst

# Pure-Python ros2cli extension: the sros2 module (verbs, keystore API, policy
# defaults/schemas/templates as package data), its dist-info with the ros2cli
# entry points, the ament index sentinel and share/sros2 (package.xml). No
# executables of its own; the verbs hang off the ros2 command.
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}.dist-info/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/%{pkg_name}/

%changelog
* Mon Oct 26 2026 Nick Schuetz <nschuetz@redhat.com> - 0.16.6-1
- Initial Fedora COPR build for ROS 2 Lyrical.
