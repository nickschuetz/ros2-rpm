%global ros_distro       lyrical
%global pkg_name         rqt_topic
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-rqt-topic
Version:        2.1.1
Release:        1%{?dist}
Summary:        ROS 2 Lyrical rqt_topic

License:        BSD-3-Clause
URL:            http://wiki.ros.org/rqt_topic
Source0:        https://github.com/ros2-gbp/rqt_topic-release/archive/refs/tags/release/lyrical/rqt_topic/2.1.1-1.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-pydantic
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  ros-lyrical-python-qt-binding
BuildRequires:  ros-lyrical-rclpy
BuildRequires:  ros-lyrical-ros2topic
BuildRequires:  ros-lyrical-rqt-gui
BuildRequires:  ros-lyrical-rqt-gui-py

Requires:       python3
Requires:       python3-pydantic
Requires:       ros-lyrical-python-qt-binding
Requires:       ros-lyrical-rclpy
Requires:       ros-lyrical-ros2topic
Requires:       ros-lyrical-rqt-gui
Requires:       ros-lyrical-rqt-gui-py

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
rqt_topic provides a GUI plugin for displaying debug information about ROS
topics including publishers, subscribers, publishing rate, and ROS
Messages.

%prep
%autosetup -p1 -n rqt_topic-release-release-lyrical-rqt_topic-2.1.1-1

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
%license LICENSE
%doc CHANGELOG.rst
%{install_prefix}/bin/*

# TODO: review the file list, generator emits a permissive glob and you may
# need to enumerate explicit paths to avoid conflicts with sibling packages.
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}.dist-info/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/%{pkg_name}/

%changelog
* Wed Jun 03 2026 Nick Schuetz <nschuetz@redhat.com> - 2.1.1-1
- Initial Fedora COPR build for ROS 2 Lyrical.
