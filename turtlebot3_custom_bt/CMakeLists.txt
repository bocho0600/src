cmake_minimum_required(VERSION 3.8)
project(turtlebot3_custom_bt)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(behaviortree_cpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(nav2_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(PkgConfig REQUIRED)
pkg_check_modules(YAML_CPP REQUIRED yaml-cpp)
find_package(nav2_msgs REQUIRED)

# Build custom BT plugin library
add_library(waypoint_bt_nodes SHARED
  src/waypoint_bt_nodes.cpp
)

# Build initial pose publisher executable
add_executable(initial_pose_publisher src/initial_pose_publisher.cpp)

target_include_directories(waypoint_bt_nodes PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

ament_target_dependencies(waypoint_bt_nodes
  rclcpp
  behaviortree_cpp
  geometry_msgs
  nav_msgs
  nav2_msgs
)

target_link_libraries(waypoint_bt_nodes ${YAML_CPP_LIBRARIES})
target_include_directories(waypoint_bt_nodes PRIVATE ${YAML_CPP_INCLUDE_DIRS})

ament_target_dependencies(initial_pose_publisher
  rclcpp
  geometry_msgs
  tf2
  tf2_geometry_msgs
)

# Install the plugin library
install(TARGETS waypoint_bt_nodes
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

# Install the executable
install(TARGETS initial_pose_publisher
  DESTINATION lib/${PROJECT_NAME}
)

# Install Python scripts
install(PROGRAMS
  src/waypoint_executor.py
  src/waypoint_executor_single.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Install directories
install(DIRECTORY behavior_trees
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY config
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Export plugin information
ament_export_libraries(waypoint_bt_nodes)
ament_export_dependencies(
  rclcpp
  behaviortree_cpp
  geometry_msgs
  nav_msgs
  nav2_msgs
)

ament_package()