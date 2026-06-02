%global ros_distro       jazzy
%global pkg_name         ament_package
%global install_prefix   /opt/ros/%{ros_distro}

Name:           ros-%{ros_distro}-ament-package
Version:        0.16.5
Release:        1%{?dist}
Summary:        ROS 2 Jazzy ament_package: build system manifest parser

License:        Apache-2.0
URL:            https://github.com/ament/ament_package
Source0:        https://github.com/ament/ament_package/archive/refs/tags/%{version}.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-setuptools
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
BuildRequires:  python3-pytest
BuildRequires:  python3-flake8

Requires:       python3

# Don't autoprovide / autorequire from /opt/ros/jazzy.
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
ament_package provides the API to parse package manifest files and
locate ament resources. It is the root of the ROS 2 ament build tooling.

%prep
%autosetup -p1 -n %{pkg_name}-%{version}

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
%pytest -v test

%files
%license LICENSE
%doc CHANGELOG.rst CONTRIBUTING.md
%{install_prefix}/lib/python%{python3_version}/site-packages/ament_package/
%{install_prefix}/lib/python%{python3_version}/site-packages/ament_package-%{version}.dist-info/
%{install_prefix}/share/ament_index/resource_index/packages/ament_package
%{install_prefix}/share/ament_package/

%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 0.16.5-1
- Initial Fedora COPR build for ROS 2 Jazzy.
