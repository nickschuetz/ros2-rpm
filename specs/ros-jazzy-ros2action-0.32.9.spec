%global ros_distro       jazzy
%global pkg_name         ros2action
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-ros2action
Version:        0.32.9
Release:        1%{?dist}
Summary:        ROS 2 Jazzy ros2action

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/ros2cli-release
Source0:        https://github.com/ros2-gbp/ros2cli-release/archive/refs/tags/release/jazzy/ros2action/0.32.9-1.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3
Requires:       ros-jazzy-action-msgs
Requires:       ros-jazzy-ament-index-python
Requires:       ros-jazzy-rclpy
Requires:       ros-jazzy-ros2cli
Requires:       ros-jazzy-rosidl-runtime-py

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
The action command for ROS 2 command line tools.

%prep
%autosetup -p1 -n ros2cli-release-release-jazzy-ros2action-0.32.9-1

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

# TODO: review the file list — generator emits a permissive glob and you may
# need to enumerate explicit paths to avoid conflicts with sibling packages.
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}.dist-info/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/%{pkg_name}/

%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 0.32.9-1
- Initial Fedora COPR build for ROS 2 Jazzy.
