import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_sim = get_package_share_directory("ros2_livox_simulation")
    pkg_point_lio = get_package_share_directory("point_lio")
    pkg_nav2_sim = get_package_share_directory("navigation2_sim")
    pkg_nav2_bringup = get_package_share_directory("nav2_bringup")
    default_prior_pcd = os.path.join(pkg_nav2_sim, "maps", "room.pcd")
    if not os.path.exists(default_prior_pcd):
        workspace_prior_pcd = os.path.abspath(
            os.path.join(
                pkg_nav2_sim, "..", "..", "..", "src", "navigation2_sim", "maps", "room.pcd"
            )
        )
        if os.path.exists(workspace_prior_pcd):
            default_prior_pcd = workspace_prior_pcd

    use_sim_time = LaunchConfiguration("use_sim_time")
    gui = LaunchConfiguration("gui")
    sim_x = LaunchConfiguration("sim_x")
    sim_y = LaunchConfiguration("sim_y")
    sim_z = LaunchConfiguration("sim_z")
    sim_yaw = LaunchConfiguration("sim_yaw")
    world = LaunchConfiguration("world")
    point_lio_cfg_dir = LaunchConfiguration("point_lio_cfg_dir")
    launch_point_lio = LaunchConfiguration("launch_point_lio")
    launch_relocalization = LaunchConfiguration("launch_relocalization")
    launch_rviz = LaunchConfiguration("launch_rviz")
    prior_pcd_file = LaunchConfiguration("prior_pcd_file")
    registered_scan_topic = LaunchConfiguration("registered_scan_topic")
    map_frame = LaunchConfiguration("map_frame")
    odom_frame = LaunchConfiguration("odom_frame")
    base_frame = LaunchConfiguration("base_frame")
    robot_base_frame = LaunchConfiguration("robot_base_frame")
    lidar_frame = LaunchConfiguration("lidar_frame")

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim, "launch", "livox_simulation.launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "gui": gui,
            "world": world,
            "x": sim_x,
            "y": sim_y,
            "z": sim_z,
            "yaw": sim_yaw,
        }.items(),
    )

    point_lio_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_point_lio, "launch", "point_lio.launch.py")
        ),
        condition=IfCondition(launch_point_lio),
        launch_arguments={
            "namespace": "",
            "rviz": "False",
            "point_lio_cfg_dir": point_lio_cfg_dir,
        }.items(),
    )

    relocalization_node = Node(
        package="small_gicp_relocalization",
        executable="small_gicp_relocalization_node",
        name="small_gicp_relocalization",
        output="screen",
        condition=IfCondition(launch_relocalization),
        remappings=[
            ("/tf", "tf"),
            ("/tf_static", "tf_static"),
            ("registered_scan", registered_scan_topic),
        ],
        parameters=[
            {
                "use_sim_time": use_sim_time,
                "num_threads": 4,
                "num_neighbors": 20,
                "global_leaf_size": 0.1,
                "registered_leaf_size": 0.05,
                "max_dist_sq": 3.0,
                "map_frame": map_frame,
                "odom_frame": odom_frame,
                "base_frame": base_frame,
                "robot_base_frame": robot_base_frame,
                "lidar_frame": lidar_frame,
                "prior_pcd_file": prior_pcd_file,
                "init_pose": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            }
        ],
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2_relocalization",
        output="screen",
        condition=IfCondition(launch_rviz),
        arguments=[
            "-d",
            os.path.join(pkg_nav2_bringup, "rviz", "nav2_default_view.rviz"),
        ],
        parameters=[{"use_sim_time": use_sim_time}],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("gui", default_value="true"),
            DeclareLaunchArgument("sim_x", default_value="2.0"),
            DeclareLaunchArgument("sim_y", default_value="1.0"),
            DeclareLaunchArgument("sim_z", default_value="0.0"),
            DeclareLaunchArgument("sim_yaw", default_value="3.14"),
            DeclareLaunchArgument(
                "world",
                description="Gazebo world name under ros2_livox_simulation/resourse/worlds, without .world suffix (required).",
            ),
            DeclareLaunchArgument(
                "point_lio_cfg_dir",
                default_value=os.path.join(pkg_point_lio, "config", "mid360.yaml"),
            ),
            DeclareLaunchArgument("launch_point_lio", default_value="true"),
            DeclareLaunchArgument("launch_relocalization", default_value="true"),
            DeclareLaunchArgument("launch_rviz", default_value="true"),
            DeclareLaunchArgument(
                "prior_pcd_file",
                default_value=default_prior_pcd,
            ),
            DeclareLaunchArgument(
                "registered_scan_topic", default_value="/cloud_registered"
            ),
            DeclareLaunchArgument("map_frame", default_value="map"),
            DeclareLaunchArgument("odom_frame", default_value="camera_init"),
            DeclareLaunchArgument("base_frame", default_value="base_link"),
            DeclareLaunchArgument("robot_base_frame", default_value="base_link"),
            DeclareLaunchArgument("lidar_frame", default_value="livox_frame"),
            sim_launch,
            point_lio_launch,
            relocalization_node,
            rviz_node,
        ]
    )
