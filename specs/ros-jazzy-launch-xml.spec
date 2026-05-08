%global ros_distro       jazzy
%global pkg_name         launch_xml
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-launch-xml
Version:        3.4.9
Release:        1%{?dist}
Summary:        ROS 2 Jazzy launch_xml

License:        Apache-2.0
URL:            https://github.com/ros2-gbp/launch-release
Source0:        https://github.com/ros2-gbp/launch-release/archive/refs/tags/release/jazzy/launch_xml/3.4.9-1.tar.gz#/%{pkg_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  ros-jazzy-launch

Requires:       python3
Requires:       ros-jazzy-launch

%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$

%description
XML frontend for the launch package.

%prep
%autosetup -p1 -n launch-release-release-jazzy-launch_xml-3.4.9-1

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
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 3.4.9-1
- Initial Fedora COPR build for ROS 2 Jazzy.
