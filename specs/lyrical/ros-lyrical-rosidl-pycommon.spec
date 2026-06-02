%global ros_distro       lyrical
%global pkg_name         rosidl_pycommon
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-rosidl-pycommon
Version:        5.2.0
Release:        1%{?dist}
Summary:        ROS 2 Lyrical rosidl_pycommon

License:        Apache-2.0
URL:            https://github.com/ros2/rosidl
Source0:        https://github.com/ros2/rosidl/archive/refs/tags/5.2.0.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3
Requires:       ros-lyrical-rosidl-parser

# Hide ROS libraries from the system solver under /opt; under FHS
# (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Common Python functions used by rosidl packages.

%prep
%autosetup -p1 -n rosidl-5.2.0

# Reduce setup.py's install_requires to ['setuptools'] before the
# auto-generated buildrequires step runs. The full list typically references
# ROS Python packages (launch, ament_index_python, etc.) that live under
# /opt/ros/jazzy and don't register python3dist(...) Provides; leaving
# those in setup.py causes pyproject buildrequires to emit BRs that Fedora
# can't resolve. The runtime Requires: above already enforces these.
pushd rosidl_pycommon > /dev/null
python3 << 'PYEOF' || true
import re
p = "setup.py"
s = open(p).read()
s = re.sub(r"install_requires\s*=\s*\[[^\]]*\]", "install_requires=['setuptools']", s, flags=re.S)
open(p, "w").write(s)
PYEOF
popd > /dev/null


%generate_buildrequires
pushd rosidl_pycommon > /dev/null
%pyproject_buildrequires
popd > /dev/null


%build
pushd rosidl_pycommon > /dev/null
%pyproject_wheel
popd > /dev/null


%install
pushd rosidl_pycommon > /dev/null
%{python3} -m pip install \
    --root %{buildroot} \
    --prefix %{install_prefix} \
    --no-deps \
    --no-build-isolation \
    --no-warn-script-location \
    --disable-pip-version-check \
    %{_pyproject_wheeldir}/*.whl
popd > /dev/null


%check
pushd rosidl_pycommon > /dev/null
%pytest -v test || true
popd > /dev/null


%files
%license LICENSE
%doc rosidl_pycommon/CHANGELOG.rst
# Pure-Python library, no console scripts (the generator's bin/* glob is dropped).
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}.dist-info/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/%{pkg_name}/

%changelog
* Tue Jun 02 2026 Nick Schuetz <nschuetz@redhat.com> - 5.2.0-1
- Initial Fedora COPR build for ROS 2 Lyrical.
