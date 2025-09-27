#include <behaviortree_cpp/action_node.h>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <rclcpp/rclcpp.hpp>

class GetNextWaypoint : public BT::SyncActionNode
{
public:
    GetNextWaypoint(const std::string &name, const BT::NodeConfiguration &config)
        : BT::SyncActionNode(name, config) {}

    static BT::PortsList providedPorts()
    {
        return {
            BT::InputPort<std::vector<geometry_msgs::msg::PoseStamped>>("waypoints"),
            BT::BidirectionalPort<int>("current_index"),
            BT::OutputPort<geometry_msgs::msg::PoseStamped>("goal"),
            BT::InputPort<bool>("loop", true, "Whether to loop back to start after finishing")
        };
    }

    BT::NodeStatus tick() override
    {
        // Get waypoints list
        auto waypoints_res = getInput<std::vector<geometry_msgs::msg::PoseStamped>>("waypoints");
        if (!waypoints_res)
        {
            throw BT::RuntimeError("GetNextWaypoint: missing input [waypoints]");
        }
        auto waypoints = waypoints_res.value();

        if (waypoints.empty())
        {
            RCLCPP_ERROR(rclcpp::get_logger("GetNextWaypoint"), "Waypoints list is empty");
            return BT::NodeStatus::FAILURE;
        }

        // Get current index (default to 0 if not set)
        int current_index = 0;
        getInput("current_index", current_index);

        // Check if we've completed all waypoints
        if (current_index >= static_cast<int>(waypoints.size()))
        {
            // Check if we should loop
            bool loop = true;
            getInput("loop", loop);
            
            if (loop)
            {
                current_index = 0;
                RCLCPP_INFO(rclcpp::get_logger("GetNextWaypoint"), "Looping back to first waypoint");
            }
            else
            {
                RCLCPP_INFO(rclcpp::get_logger("GetNextWaypoint"), "All waypoints completed, no looping");
                return BT::NodeStatus::FAILURE;
            }
        }

        // Get current waypoint
        geometry_msgs::msg::PoseStamped current_goal = waypoints[current_index];
        current_goal.header.stamp = rclcpp::Clock().now();

        // Set outputs
        setOutput("goal", current_goal);
        setOutput("current_index", current_index + 1);

        RCLCPP_INFO(rclcpp::get_logger("GetNextWaypoint"), 
                   "Setting waypoint %d: (%.2f, %.2f, %.2f)", 
                   current_index,
                   current_goal.pose.position.x,
                   current_goal.pose.position.y,
                   atan2(2.0 * current_goal.pose.orientation.w * current_goal.pose.orientation.z,
                         1.0 - 2.0 * current_goal.pose.orientation.z * current_goal.pose.orientation.z));

        return BT::NodeStatus::SUCCESS;
    }
};