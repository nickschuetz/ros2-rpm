%global ros_distro       jazzy
%global install_prefix   /opt/ros/jazzy

Name:           ros-%{ros_distro}-ros-desktop
Version:        0.13.0
Release:        1%{?dist}
Summary:        ROS 2 Jazzy dev-sandbox install — ros-base plus rqt, ros2cli, launch, demos

# Heterogeneous license aggregate, honestly disclosed per ADR 0011.
# - Apache-2.0 / BSD-3-Clause: ros-base contents (rclcpp, tf2, message packages, etc.).
# - LGPL-3.0: Qt5 (via rqt suite for visualization / debug GUIs).
License:        Apache-2.0 AND BSD-3-Clause AND LGPL-3.0
URL:            https://github.com/nickschuetz/ros2-rpm
Source0:        ros-jazzy-ros-desktop-%{version}.tar.gz

BuildArch:      noarch

# Pulls in the full ros-base (Phase 1 scope: rclcpp, tf2, common message
# packages, Fast DDS RMW).
Requires:       ros-jazzy-ros-base = %{version}-%{release}

# launch infrastructure (Phase 2 P-2).
Requires:       ros-jazzy-launch
Requires:       ros-jazzy-launch-ros
Requires:       ros-jazzy-launch-xml
Requires:       ros-jazzy-launch-yaml
Requires:       ros-jazzy-launch-testing
Requires:       ros-jazzy-osrf-pycommon

# ros2cli + per-domain CLI plugins (Phase 2 P-2).
Requires:       ros-jazzy-ros2cli
Requires:       ros-jazzy-ros2pkg
Requires:       ros-jazzy-ros2run
Requires:       ros-jazzy-ros2node
Requires:       ros-jazzy-ros2topic
Requires:       ros-jazzy-ros2service
Requires:       ros-jazzy-ros2interface
Requires:       ros-jazzy-ros2action
Requires:       ros-jazzy-ros2lifecycle
Requires:       ros-jazzy-ros2param
Requires:       ros-jazzy-ros2component

# rqt + plugins (Phase 2 P-3, Fedora-only — Stream 10 lacks Qt5/sip-devel).
# These pull LGPL-3.0 via Qt5 — the package's License: aggregate above is
# the disclosure. Users explicitly opt in by installing ros-jazzy-ros-desktop.
Requires:       ros-jazzy-rqt
Requires:       ros-jazzy-rqt-gui
Requires:       ros-jazzy-rqt-gui-py
Requires:       ros-jazzy-rqt-graph
Requires:       ros-jazzy-rqt-topic
Requires:       ros-jazzy-rqt-console
Requires:       ros-jazzy-rqt-publisher
Requires:       ros-jazzy-rqt-service-caller
Requires:       ros-jazzy-rqt-action
Requires:       ros-jazzy-rqt-plot

# rcl_lifecycle + rclcpp_lifecycle for component lifecycle development (P-2 backfill).
Requires:       ros-jazzy-rcl-lifecycle
Requires:       ros-jazzy-rclcpp-lifecycle
Requires:       ros-jazzy-lifecycle-msgs

# Demo nodes for environment verification (Phase 2 P-5).
Requires:       ros-jazzy-demo-nodes-cpp
Requires:       ros-jazzy-demo-nodes-py
Requires:       ros-jazzy-example-interfaces

%description
Default desktop-style install for ROS 2 Jazzy users on this development-only
COPR. Pulls in ros-base plus the launch infrastructure, ros2 CLI suite, rqt
visualization + debug GUIs, and demo_nodes for environment verification.

This metapackage carries a heterogeneous license aggregate including LGPL-3.0
(Qt5 via the rqt suite). Installing this package is an explicit opt-in to
that aggregate. ros-jazzy-ros-base remains permissive-only (Apache-2.0 AND
BSD-3-Clause) for users who want the smaller default.

Phase 2 dev-sandbox per ADR 0011 — not the official ROS 2 packages for
Fedora; Open Robotics's official Lyrical packages are the production path.

Note: Phase 2 GUI packages (rqt suite) build on Fedora chroots only; CentOS
Stream 10 ships without the Qt5 build deps required by python_qt_binding.
On Stream 10, install ros-jazzy-ros-base instead.

Note: rviz2 is **not** included in this metapackage — its Ogre and Assimp
vendor builds need workarounds for CMake 4.x and Fedora's GCC -Werror that
have not landed in upstream rviz_*_vendor. Tracked for a future iteration.

%prep
# No source — pure metapackage.

%build
# Nothing to build.

%install
mkdir -p %{buildroot}%{install_prefix}
echo "ros-jazzy-ros-desktop %{version} (metapackage)" > %{buildroot}%{install_prefix}/.ros-desktop-version

%files
%{install_prefix}/.ros-desktop-version

%changelog
* Fri May 08 2026 Nick Schuetz <nschuetz@redhat.com> - 0.13.0-1
- Initial Phase 2 dev-sandbox metapackage. Heterogeneous license aggregate
  (Apache-2.0 AND BSD-3-Clause AND LGPL-3.0 via Qt5) honestly disclosed
  per ADR 0011.
