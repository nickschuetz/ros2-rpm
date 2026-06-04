#!/usr/bin/env bash
# scripts/smoke-test.sh, end-to-end install validation for the hellaenergy ROS 2 COPRs
#
# Run after `dnf install ros-<distro>-ros-base` (and optionally
# ros-<distro>-ros2cli + ros-<distro>-demo-nodes-cpp) to confirm the install is
# functional. Prints PASS / FAIL per check. Returns non-zero on first FAIL.
#
# Usage:
#   bash scripts/smoke-test.sh [distro] [-v]
#     distro   lyrical (default, flagship) or jazzy (maintenance)
#     -v       verbose: show command output on PASS too
#
# Exit codes:
#   0  every check that ran passed
#   1  one or more checks failed
#   2  prerequisites missing (ros-base not installed, setup.bash missing, etc.)
#
# This is a *user* smoke test, not a developer regression suite. It works
# against any /opt/ros/<distro>/ install regardless of where the RPMs came
# from: the hellaenergy COPRs, the Fedora Robotics SIG's repos
# (https://docs.fedoraproject.org/en-US/robotics-sig/ros2/), or
# packages.ros.org's RHEL 9 RPMs. The check assumptions are:
# - You're on Fedora 44+ or CentOS Stream 10 (or a RHEL 9 derivative
#   if you're using packages.ros.org).
# - You've installed at minimum `ros-<distro>-ros-base`.
# - /opt/ros/<distro>/ is writable to root only (don't run this as root;
#   the test never needs root).

set -uo pipefail

VERBOSE=0
DISTRO=""
for arg in "$@"; do
    case "$arg" in
        -v) VERBOSE=1 ;;
        lyrical|jazzy) DISTRO="$arg" ;;
        *) echo "Unknown argument: $arg (expected: lyrical|jazzy and/or -v)" >&2; exit 2 ;;
    esac
done
DISTRO="${DISTRO:-lyrical}"
export ROS_PREFIX="/opt/ros/${DISTRO}"
export ROS_DISTRO_EXPECT="${DISTRO}"

PYTHON_VERSION=${PYTHON_VERSION:-$(python3 -c "import sys;print(f'{sys.version_info.major}.{sys.version_info.minor}')")}

PASS=0
FAIL=0
SKIP=0

green() { printf "\033[32m%s\033[0m" "$*"; }
red()   { printf "\033[31m%s\033[0m" "$*"; }
yellow(){ printf "\033[33m%s\033[0m" "$*"; }

check() {
    local name="$1"
    shift

    if [ "$VERBOSE" = "1" ]; then
        printf "  ▸ %-55s ... " "$name"
        if "$@"; then
            green "PASS"
            echo
            PASS=$((PASS + 1))
            return 0
        else
            red "FAIL"
            echo
            FAIL=$((FAIL + 1))
            return 1
        fi
    fi
    if "$@" >/dev/null 2>&1; then
        printf "  ▸ %-55s ... %s\n" "$name" "$(green PASS)"
        PASS=$((PASS + 1))
    else
        printf "  ▸ %-55s ... %s\n" "$name" "$(red FAIL)"
        FAIL=$((FAIL + 1))
    fi
}

skip() {
    local name="$1"
    local reason="$2"
    printf "  ▸ %-55s ... %s (%s)\n" "$name" "$(yellow SKIP)" "$reason"
    SKIP=$((SKIP + 1))
}

section() {
    echo
    echo "── $* ──"
}

echo "ROS 2 ${DISTRO} smoke test (prefix ${ROS_PREFIX})"

#-----------------------------------------------------------------------
# Section 1, install presence
#-----------------------------------------------------------------------
section "Install presence"

check "ros-${DISTRO}-ros-base RPM installed" \
    rpm -q "ros-${DISTRO}-ros-base"

check "${ROS_PREFIX}/setup.bash exists" \
    test -f "${ROS_PREFIX}/setup.bash"

check "${ROS_PREFIX}/lib/librclcpp.so* present" \
    bash -c 'compgen -G "${ROS_PREFIX}/lib/librclcpp.so*" > /dev/null'

check "libfoonathan_memory present under ${ROS_PREFIX} (lib or lib64)" \
    bash -c "find '${ROS_PREFIX}' -name 'libfoonathan_memory*' 2>/dev/null | grep -Eq 'libfoonathan_memory-[0-9.]+\.so'"

check "rclpy package layout" \
    test -d "${ROS_PREFIX}/lib/python${PYTHON_VERSION}/site-packages/rclpy" 2>/dev/null


if [ "$FAIL" -gt 0 ]; then
    echo
    red "FATAL: install presence checks failed."
    echo
    echo "  Make sure you ran:"
    if [ "$DISTRO" = "lyrical" ]; then
        echo "    sudo dnf copr enable -y hellaenergy/ros2"
    else
        echo "    sudo dnf copr enable -y hellaenergy/ros2-${DISTRO}"
    fi
    echo "    sudo dnf install -y ros-${DISTRO}-ros-base"
    exit 2
fi

#-----------------------------------------------------------------------
# Section 2, environment activation
#-----------------------------------------------------------------------
section "Environment activation"

# Source setup.bash in a subshell and exfiltrate the env vars we care about.
# We can't `source` in this script directly because the test runs a sequence
# of these and a borked source could hose later checks.
SETUP_OUTPUT=$(bash -c 'source "${ROS_PREFIX}/setup.bash" >/dev/null 2>&1
echo "ROS_DISTRO=$ROS_DISTRO"
echo "AMENT_PREFIX_PATH=$AMENT_PREFIX_PATH"
echo "PATH_HAS_ROS=$(echo $PATH | grep -c ${ROS_PREFIX}/bin)"
echo "PYTHONPATH_HAS_ROS=$(echo $PYTHONPATH | grep -c ${ROS_PREFIX})"' 2>&1)

check "setup.bash sets ROS_DISTRO=${DISTRO}" \
    bash -c "echo '$SETUP_OUTPUT' | grep -q 'ROS_DISTRO=${ROS_DISTRO_EXPECT}'"

check "setup.bash sets AMENT_PREFIX_PATH" \
    bash -c "echo '$SETUP_OUTPUT' | grep -q 'AMENT_PREFIX_PATH=.*opt/ros/${DISTRO}'"

check "setup.bash adds ${ROS_PREFIX}/bin to PATH" \
    bash -c "echo '$SETUP_OUTPUT' | grep -q 'PATH_HAS_ROS=[1-9]'"

#-----------------------------------------------------------------------
# Section 3, Python bindings
#-----------------------------------------------------------------------
section "Python bindings (rclpy)"

if rpm -q "ros-${DISTRO}-rclpy" >/dev/null 2>&1; then
    check "import rclpy" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && python3 -c "import rclpy"'
    check "import std_msgs.msg" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && python3 -c "import std_msgs.msg; std_msgs.msg.String()"'
    check "import geometry_msgs.msg" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && python3 -c "import geometry_msgs.msg; geometry_msgs.msg.Twist()"'
    check "import sensor_msgs.msg" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && python3 -c "import sensor_msgs.msg; sensor_msgs.msg.Imu()"'
    check "rclpy.init() + create_node + shutdown" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && python3 -c "
import rclpy
rclpy.init()
node = rclpy.create_node(\"hellaenergy_smoketest_py\")
node.destroy_node()
rclpy.shutdown()
"'
else
    skip "rclpy checks" "ros-${DISTRO}-rclpy not installed"
fi

#-----------------------------------------------------------------------
# Section 4, C++ build + run
#-----------------------------------------------------------------------
section "C++ rclcpp (compile + run)"

if ! command -v cmake >/dev/null 2>&1 || ! command -v g++ >/dev/null 2>&1; then
    skip "rclcpp C++ build" "cmake or g++ not on PATH"
else
    BUILD_DIR=$(mktemp -d -t hellaenergy-smoketest.XXXXXX)
    trap 'rm -rf "$BUILD_DIR"' EXIT

    cat > "$BUILD_DIR/main.cpp" <<'EOF'
#include <rclcpp/rclcpp.hpp>
int main(int argc, char ** argv) {
    rclcpp::init(argc, argv);
    auto n = std::make_shared<rclcpp::Node>("hellaenergy_smoketest_cpp");
    RCLCPP_INFO(n->get_logger(), "rclcpp OK");
    rclcpp::shutdown();
    return 0;
}
EOF

    # Link with the modern ${rclcpp_TARGETS} form rather than the legacy
    # ament_target_dependencies() macro: the latter was deprecated in Jazzy and
    # removed upstream by Lyrical (ament_cmake_target_dependencies no longer
    # ships ament_target_dependencies.cmake), so it is "Unknown CMake command"
    # there. ${rclcpp_TARGETS} works on both Jazzy and Lyrical.
    cat > "$BUILD_DIR/CMakeLists.txt" <<'EOF'
cmake_minimum_required(VERSION 3.10)
project(smoketest)
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
add_executable(smoketest main.cpp)
target_link_libraries(smoketest ${rclcpp_TARGETS})
EOF

    check "rclcpp CMake configure" \
        bash -c "source '${ROS_PREFIX}/setup.bash' && cd '$BUILD_DIR' && \
                 cmake -DCMAKE_PREFIX_PATH='${ROS_PREFIX}' -S . -B build"
    check "rclcpp build" \
        bash -c "source '${ROS_PREFIX}/setup.bash' && cd '$BUILD_DIR' && \
                 cmake --build build"
    check "rclcpp run (rclcpp::init / shutdown)" \
        bash -c "source '${ROS_PREFIX}/setup.bash' && '$BUILD_DIR/build/smoketest'"
fi

#-----------------------------------------------------------------------
# Section 5, ros2 CLI (only if ros2cli is installed)
#-----------------------------------------------------------------------
section "ros2 CLI"

if rpm -q "ros-${DISTRO}-ros2cli" >/dev/null 2>&1; then
    check "which ros2 finds ${ROS_PREFIX}/bin/ros2" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && which ros2 | grep -q "${ROS_PREFIX}/bin/ros2"'
    check "ros2 --help runs without error" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && ros2 --help > /dev/null'
    if rpm -q "ros-${DISTRO}-ros2topic" >/dev/null 2>&1; then
        check "ros2 topic list returns daemon topics" \
            bash -c 'source "${ROS_PREFIX}/setup.bash" && \
                     timeout 5 ros2 topic list 2>/dev/null | grep -q rosout'
    else
        skip "ros2 topic list" "ros-${DISTRO}-ros2topic not installed"
    fi
else
    skip "ros2 CLI checks" "ros-${DISTRO}-ros2cli not installed"
fi

#-----------------------------------------------------------------------
# Section 6, demo_nodes (talker actually publishes)
#-----------------------------------------------------------------------
section "Demo nodes (publish path)"

if rpm -q "ros-${DISTRO}-demo-nodes-cpp" >/dev/null 2>&1; then
    check "demo_nodes_cpp/talker publishes 'Hello World'" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && \
                 timeout 3 "${ROS_PREFIX}/lib/demo_nodes_cpp/talker" 2>&1 | \
                 grep -q "Hello World"'
else
    skip "talker check" "ros-${DISTRO}-demo-nodes-cpp not installed"
fi

#-----------------------------------------------------------------------
# Section 7, O3DE Gem optional dep (gazebo_msgs)
#-----------------------------------------------------------------------
section "O3DE Gem optional dep (gazebo_msgs)"

if rpm -q "ros-${DISTRO}-gazebo-msgs" >/dev/null 2>&1; then
    check "import gazebo_msgs.msg.ContactState" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && \
                 python3 -c "import gazebo_msgs.msg; gazebo_msgs.msg.ContactState()"'
    check "import gazebo_msgs.srv.SpawnEntity" \
        bash -c 'source "${ROS_PREFIX}/setup.bash" && \
                 python3 -c "import gazebo_msgs.srv; gazebo_msgs.srv.SpawnEntity.Request()"'
else
    skip "gazebo_msgs checks" "ros-${DISTRO}-gazebo-msgs not installed (optional, gates O3DE Gem ContactSensor + Spawner)"
fi

#-----------------------------------------------------------------------
# Summary
#-----------------------------------------------------------------------
echo
echo "──"
TOTAL=$((PASS + FAIL))
printf "  %s passed, %s failed, %s skipped (%s checks ran)\n" \
    "$(green $PASS)" \
    "$(test "$FAIL" -gt 0 && red "$FAIL" || echo "$FAIL")" \
    "$(yellow $SKIP)" \
    "$TOTAL"

if [ "$FAIL" -eq 0 ]; then
    echo
    green "All checks passed."
    echo
    echo
    echo "Your ROS 2 ${DISTRO} install is functional. Source the workspace with:"
    echo "  source ${ROS_PREFIX}/setup.bash"
    exit 0
else
    echo
    red "$FAIL check(s) failed."
    echo
    echo
    echo "Re-run with -v to see command output:"
    echo "  bash $0 ${DISTRO} -v"
    echo
    echo "If the failures are reproducible, please open an issue:"
    echo "  https://github.com/nickschuetz/ros2-rpm/issues/new"
    exit 1
fi
