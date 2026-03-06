import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import PushRosNamespace, SetRemap


def generate_launch_description():
    # Get the launch directory
    pkg_robot_description_dir = get_package_share_directory(
        "ros2_livox_simulation"
    )

    use_sim_time = LaunchConfiguration("use_sim_time")
    robot_name = LaunchConfiguration("robot_name")

    # Declare the launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation (Gazebo) clock if true",
    )

    declare_robot_name_cmd = DeclareLaunchArgument(
        "robot_name",
        default_value="myrobot",
        description="The file name of the robot ",
    )

    bringup_cmd_group = GroupAction(
        [
            SetRemap("/tf", "tf"),
            SetRemap("/tf_static", "tf_static"),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(
                        pkg_robot_description_dir,
                        "launch",
                        "description.launch.py",
                    )
                ),
                launch_arguments={
                    "use_sim_time": use_sim_time,
                    "robot_name": robot_name,
                    "use_rviz": "False",
                }.items(),
            ),
        ]
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_use_sim_time_cmd)
    ld.add_action(declare_robot_name_cmd)

    # Add the actions to launch all nodes
    ld.add_action(bringup_cmd_group)

    return ld
