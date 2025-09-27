#include <behaviortree_cpp/bt_factory.h>
#include "load_waypoints.cpp"
#include "get_next_waypoint.cpp"

// Plugin to register custom BT nodes with Nav2
BT_REGISTER_NODES(factory)
{
    factory.registerNodeType<LoadWaypoints>("LoadWaypoints");
    factory.registerNodeType<GetNextWaypoint>("GetNextWaypoint");
}