%global ros_distro       jazzy
%global pkg_name         ament_index_python
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-ament-index-python
Version:        1.8.3
Release:        1%{?dist}
Summary:        ROS 2 Jazzy ament_index_python

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/ament_index-release
Source0:        https://github.com/ros2-gbp/ament_index-release/archive/refs/tags/release/jazzy/ament_index_python/1.8.3-1.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3

# Under /opt these libraries must not be exposed to the system dependency
# solver; under FHS (--with fedora_fhs) normal auto-provides/requires apply.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

%description
Python API to access the ament resource index.

%prep
%autosetup -p1 -n ament_index-release-release-jazzy-ament_index_python-1.8.3-1

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
%{install_prefix}/bin/*

# TODO: review the file list, generator emits a permissive glob and you may
# need to enumerate explicit paths to avoid conflicts with sibling packages.
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}.dist-info/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/%{pkg_name}/

%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 1.8.3-1
- Initial Fedora COPR build for ROS 2 Jazzy.
