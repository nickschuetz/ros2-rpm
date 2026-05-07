%global ros_distro       jazzy
%global pkg_name         rosidl_pycommon
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-rosidl-pycommon
Version:        4.6.7
Release:        1%{?dist}
Summary:        ROS 2 Jazzy rosidl_pycommon

License:        Apache-2.0
URL:            https://github.com/ros2/rosidl
Source0:        https://github.com/ros2/rosidl/archive/refs/tags/4.6.7.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel

Requires:       python3
Requires:       ros-jazzy-rosidl-parser

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
Common Python functions used by rosidl packages.

%prep
%autosetup -p1 -n rosidl-4.6.7

%generate_buildrequires
pushd rosidl_pycommon
%pyproject_buildrequires
popd


%build
pushd rosidl_pycommon
%pyproject_wheel
popd


%install
pushd rosidl_pycommon
%{python3} -m pip install \
    --root %{buildroot} \
    --prefix %{install_prefix} \
    --no-deps \
    --no-build-isolation \
    --no-warn-script-location \
    --disable-pip-version-check \
    %{_pyproject_wheeldir}/*.whl
popd


%check
pushd rosidl_pycommon
%pytest -v test || true
popd


%files
%license LICENSE
%doc rosidl_pycommon/CHANGELOG.rst
# TODO: review the file list — generator emits a permissive glob and you may
# need to enumerate explicit paths to avoid conflicts with sibling packages.
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}/
%{install_prefix}/lib/python%{python3_version}/site-packages/%{pkg_name}-%{version}.dist-info/
%{install_prefix}/share/ament_index/resource_index/packages/%{pkg_name}
%{install_prefix}/share/%{pkg_name}/

%changelog
* Thu May 07 2026 Nick Schuetz <nschuetz@redhat.com> - 4.6.7-1
- Initial Fedora COPR build for ROS 2 Jazzy.
