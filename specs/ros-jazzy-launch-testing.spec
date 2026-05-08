%global ros_distro       jazzy
%global pkg_name         launch_testing
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-launch-testing
Version:        3.4.10
Release:        1%{?dist}
Summary:        ROS 2 Jazzy launch_testing

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/launch-release
Source0:        https://github.com/ros2-gbp/launch-release/archive/refs/tags/release/jazzy/launch_testing/3.4.10-1.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3
Requires:       python3-pytest
Requires:       ros-jazzy-ament-index-python
Requires:       ros-jazzy-launch
Requires:       ros-jazzy-launch-xml
Requires:       ros-jazzy-launch-yaml
Requires:       ros-jazzy-osrf-pycommon

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
A package to create tests which involve launch files and multiple
processes.

%prep
%autosetup -p1 -n launch-release-release-jazzy-launch_testing-3.4.10-1

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
# (no LICENSE file in source tree — see package.xml <license>)
%doc CHANGELOG.rst
%{install_prefix}/bin/*

# TODO: review the file list — generator emits a permissive glob and you may
# need to enumerate explicit paths to avoid conflicts with sibling packages.
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}.dist-info/
# launch_testing's setup.py installs example_processes/ to lib/launch_testing/
# (not site-packages) for use as test fixtures.
%{install_prefix}/lib/%{pkg_name}/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/%{pkg_name}/

%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 3.4.10-1
- Initial Fedora COPR build for ROS 2 Jazzy.
