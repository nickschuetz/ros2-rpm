%global ros_distro       lyrical
%bcond fedora_fhs 0
%if %{with fedora_fhs}
# FHS layout for a possible Fedora main-repo build or reference impl (ADR 0012).
%global install_prefix   %{_prefix}
%else
# COPR default: upstream ROS 2 /opt convention.
%global install_prefix   /opt/ros/%{ros_distro}
%endif

Name:           ros-%{ros_distro}-ros-desktop
Version:        0.13.1
Release:        1%{?dist}
Summary:        ROS 2 Lyrical dev-sandbox install, ros-base plus rqt, ros2cli, launch, rviz2, demos

# Heterogeneous license aggregate, honestly disclosed per ADR 0011.
# - Apache-2.0 / BSD-3-Clause: ros-base contents (rclcpp, tf2, message packages, etc.).
# - LGPL-3.0: Qt6 (via the rqt suite and rviz2 for visualization / debug GUIs).
# - EPL-2.0: eclipse-cyclonedds (the alternate Cyclone DDS RMW).
License:        Apache-2.0 AND BSD-3-Clause AND LGPL-3.0-only AND EPL-2.0
URL:            https://github.com/nickschuetz/ros2-rpm

BuildArch:      noarch

# Hide the metapackage marker file from the system solver under /opt.
%if %{without fedora_fhs}
%global __provides_exclude_from ^%{install_prefix}/.*$
%global __requires_exclude_from ^%{install_prefix}/.*$
%endif

# Pulls in the full ros-base (rclcpp, tf2, common message packages, Fast DDS RMW).
Requires:       ros-lyrical-ros-base

# launch infrastructure.
Requires:       ros-lyrical-launch
Requires:       ros-lyrical-launch-ros
Requires:       ros-lyrical-launch-xml
Requires:       ros-lyrical-launch-yaml
Requires:       ros-lyrical-launch-testing
Requires:       ros-lyrical-osrf-pycommon

# ros2cli + per-domain CLI plugins.
Requires:       ros-lyrical-ros2cli
Requires:       ros-lyrical-ros2pkg
Requires:       ros-lyrical-ros2run
Requires:       ros-lyrical-ros2node
Requires:       ros-lyrical-ros2topic
Requires:       ros-lyrical-ros2service
Requires:       ros-lyrical-ros2interface
Requires:       ros-lyrical-ros2action
Requires:       ros-lyrical-ros2lifecycle
Requires:       ros-lyrical-ros2param
Requires:       ros-lyrical-ros2component

# rqt + plugins. These pull LGPL-3.0 via Qt6; the package's License: aggregate
# above is the disclosure. Users explicitly opt in by installing this package.
Requires:       ros-lyrical-rqt
Requires:       ros-lyrical-rqt-gui
Requires:       ros-lyrical-rqt-gui-py
Requires:       ros-lyrical-rqt-graph
Requires:       ros-lyrical-rqt-topic
Requires:       ros-lyrical-rqt-console
Requires:       ros-lyrical-rqt-publisher
Requires:       ros-lyrical-rqt-service-caller
Requires:       ros-lyrical-rqt-action
Requires:       ros-lyrical-rqt-plot

# rviz2 3D visualization (LGPL-3.0 via Qt6). Builds on Fedora 44 and CentOS
# Stream 10 only; fedora-rawhide is deferred (vcstool/pkg_resources breakage in
# the Ogre and gz vendor ExternalProject downloads under Python 3.14).
Requires:       ros-lyrical-rviz2
Requires:       ros-lyrical-rviz-common
Requires:       ros-lyrical-rviz-default-plugins
Requires:       ros-lyrical-interactive-markers

# Cyclone DDS as an alternate RMW (EPL-2.0). Opt-in via this metapackage.
Requires:       ros-lyrical-cyclonedds
Requires:       ros-lyrical-rmw-cyclonedds-cpp

# rcl_lifecycle + rclcpp_lifecycle for component lifecycle development.
Requires:       ros-lyrical-rcl-lifecycle
Requires:       ros-lyrical-rclcpp-lifecycle
Requires:       ros-lyrical-lifecycle-msgs

# Demo nodes for environment verification.
Requires:       ros-lyrical-demo-nodes-cpp
Requires:       ros-lyrical-demo-nodes-py
Requires:       ros-lyrical-example-interfaces

%description
Default desktop-style install for ROS 2 Lyrical users on this development-only
COPR. Pulls in ros-base plus the launch infrastructure, ros2 CLI suite, rqt
visualization + debug GUIs, rviz2, the Cyclone DDS alternate RMW, and
demo_nodes for environment verification.

This metapackage carries a heterogeneous license aggregate including LGPL-3.0
(Qt6 via the rqt suite and rviz2) and EPL-2.0 (Cyclone DDS). Installing this
package is an explicit opt-in to that aggregate. ros-lyrical-ros-base remains
permissive-only (Apache-2.0 AND BSD-3-Clause) for users who want the smaller
default.

Phase 2 dev-sandbox per ADR 0011, not the official ROS 2 packages for
Fedora; Open Robotics's official Lyrical packages are the production path.

Note: this metapackage and its rviz2 dependency build on Fedora 44 and CentOS
Stream 10 only. fedora-rawhide is deferred because the Ogre and Gazebo vendor
ExternalProject downloads use vcstool, which is broken on rawhide's Python 3.14
(setuptools dropped pkg_resources). On rawhide, install ros-lyrical-ros-base.

%prep
# No source, pure metapackage.

%build
# Nothing to build.

%install
mkdir -p %{buildroot}%{install_prefix}
echo "ros-lyrical-ros-desktop %{version} (metapackage)" > %{buildroot}%{install_prefix}/.ros-desktop-version

%files
%{install_prefix}/.ros-desktop-version

%changelog
* Fri Jun 05 2026 Nick Schuetz <nschuetz@redhat.com> - 0.13.1-1
- Initial Lyrical Phase 2 dev-sandbox metapackage. Adds rviz2 and the Cyclone
  DDS alternate RMW on top of the Jazzy dev-sandbox set. Heterogeneous license
  aggregate (Apache-2.0 AND BSD-3-Clause AND LGPL-3.0 via Qt6 AND EPL-2.0 via
  Cyclone DDS) honestly disclosed per ADR 0011.
