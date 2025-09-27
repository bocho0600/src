#include <behaviortree_cpp/action_node.h>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <yaml-cpp/yaml.h>
#include <rclcpp/rclcpp.hpp>
#include <cmath>

class LoadWaypoints : public BT::SyncActionNode
{
public:
    LoadWaypoints(const std::string &name, const BT::NodeConfiguration &config)
        : BT::SyncActionNode(name, config) {}

    // Required: provide ports (inputs/outputs)
    static BT::PortsList providedPorts()
    {
        return {
            BT::InputPort<std::string>("file"),
            BT::OutputPort<std::vector<geometry_msgs::msg::PoseStamped>>("waypoints")
        };
    }

    BT::NodeStatus tick() override
    {
        // Get YAML file path
        auto res = getInput<std::string>("file");
        if (!res)
        {
            throw BT::RuntimeError("LoadWaypoints: missing input [file]");
        }
        std::string file_path = res.value();

        try {
            // Parse YAML
            YAML::Node yaml = YAML::LoadFile(file_path);
            std::vector<geometry_msgs::msg::PoseStamped> waypoints;

            if (!yaml["waypoints"])
            {
                RCLCPP_ERROR(rclcpp::get_logger("LoadWaypoints"), "No 'waypoints' key in YAML file");
                return BT::NodeStatus::FAILURE;
            }

            for (const auto &wp : yaml["waypoints"])
            {
                geometry_msgs::msg::PoseStamped pose;
                pose.header.frame_id = "map";  // or global frame
                pose.header.stamp = rclcpp::Clock().now();
                pose.pose.position.x = wp["x"].as<double>();
                pose.pose.position.y = wp["y"].as<double>();
                pose.pose.position.z = 0.0;

                // Convert yaw to quaternion
                double theta = wp["theta"].as<double>();
                pose.pose.orientation.w = cos(theta / 2.0);
                pose.pose.orientation.z = sin(theta / 2.0);
                pose.pose.orientation.x = 0.0;
                pose.pose.orientation.y = 0.0;

                waypoints.push_back(pose);
            }

            // Write to blackboard
            setOutput("waypoints", waypoints);

            RCLCPP_INFO(rclcpp::get_logger("LoadWaypoints"), "Loaded %zu waypoints from %s", 
                       waypoints.size(), file_path.c_str());
            return BT::NodeStatus::SUCCESS;
        } 
        catch (const YAML::Exception& e) 
        {
            RCLCPP_ERROR(rclcpp::get_logger("LoadWaypoints"), "YAML parsing error: %s", e.what());
            return BT::NodeStatus::FAILURE;
        }
        catch (const std::exception& e)
        {
            RCLCPP_ERROR(rclcpp::get_logger("LoadWaypoints"), "Error loading waypoints: %s", e.what());
            return BT::NodeStatus::FAILURE;
        }
    }
};