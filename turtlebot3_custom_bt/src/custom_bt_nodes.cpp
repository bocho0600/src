#include <behaviortree_cpp/bt_factory.h>
#include <rclcpp/rclcpp.hpp>

// Include all your custom BT nodes
#include "load_waypoints.cpp"
#include "get_next_waypoint.cpp"

// Plugin to register custom BT nodes with Nav2
BT_REGISTER_NODES(factory)
{
    factory.registerNodeType<LoadWaypoints>("LoadWaypoints");
    factory.registerNodeType<GetNextWaypoint>("GetNextWaypoint");
}