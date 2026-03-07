import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_bringup_dir = get_package_share_directory("RC2026_bringup")
    pkg_point_lio_dir = get_package_share_directory("point_lio")
    pkg_nav2_dir = get_package_share_directory("navigation2_sim")
    pkg_livox_sim_dir = get_package_share_directory("ros2_livox_simulation")

    use_sim_time = LaunchConfiguration("use_sim_time")
    sim_x = LaunchConfiguration("sim_x")
    sim_y = LaunchConfiguration("sim_y")
    sim_z = LaunchConfiguration("sim_z")
    sim_yaw = LaunchConfiguration("sim_yaw")
    sim_world = LaunchConfiguration("world")
    point_lio_cfg_dir = LaunchConfiguration("point_lio_cfg_dir")
    map_yaml = LaunchConfiguration("map")
    nav2_params_file = LaunchConfiguration("nav2_params_file")
    launch_nav2 = LaunchConfiguration("launch_nav2")
    launch_relocalization = LaunchConfiguration("launch_relocalization")
    prior_pcd_file = LaunchConfiguration("prior_pcd_file")
    registered_scan_topic = LaunchConfiguration("registered_scan_topic")
    map_frame = LaunchConfiguration("map_frame")
    odom_frame = LaunchConfiguration("odom_frame")
    base_frame = LaunchConfiguration("base_frame")
    robot_base_frame = LaunchConfiguration("robot_base_frame")
    lidar_frame = LaunchConfiguration("lidar_frame")

    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation clock if true.",
    )
    declare_sim_x = DeclareLaunchArgument(
        "sim_x",
        default_value="2.0",
        description="Spawn x for livox simulation.",
    )
    declare_sim_y = DeclareLaunchArgument(
        "sim_y",
        default_value="1.0",
        description="Spawn y for livox simulation.",
    )
    declare_sim_z = DeclareLaunchArgument(
        "sim_z",
        default_value="0.0",
        description="Spawn z for livox simulation.",
    )
    declare_sim_yaw = DeclareLaunchArgument(
        "sim_yaw",
        default_value="3.14",
        description="Spawn yaw(rad) for livox simulation.",
    )
    declare_world = DeclareLaunchArgument(
        "world",
        description="Gazebo world name under ros2_livox_simulation/resourse/worlds, without .world suffix (required).",
    )
    declare_point_lio_cfg = DeclareLaunchArgument(
        "point_lio_cfg_dir",
        default_value=os.path.join(pkg_point_lio_dir, "config", "mid360.yaml"),
        description="Path to Point-LIO yaml.",
    )
    declare_map_yaml = DeclareLaunchArgument(
        "map",
        default_value=os.path.join(pkg_bringup_dir, "map", "room.yaml"),
        description="Path to nav2 map yaml.",
    )
    declare_nav2_params = DeclareLaunchArgument(
        "nav2_params_file",
        default_value=os.path.join(pkg_bringup_dir, "config", "nav2_params.yaml"),
        description="Path to nav2 params yaml.",
    )
    declare_launch_nav2 = DeclareLaunchArgument(
        "launch_nav2",
        default_value="true",
        description="Launch nav2 stack.",
    )
    declare_launch_relocalization = DeclareLaunchArgument(
        "launch_relocalization",
        default_value="true",
        description="Launch small_gicp relocalization node.",
    )
    declare_prior_pcd_file = DeclareLaunchArgument(
        "prior_pcd_file",
        default_value=os.path.join(pkg_nav2_dir, "maps", "room.pcd"),
        description="Path to prior map pcd for relocalization.",
    )
    declare_registered_scan_topic = DeclareLaunchArgument(
        "registered_scan_topic",
        default_value="/cloud_registered",
        description="Registered point cloud topic used by relocalization.",
    )
    declare_map_frame = DeclareLaunchArgument(
        "map_frame",
        default_value="map",
        description="Map frame for relocalization.",
    )
    declare_odom_frame = DeclareLaunchArgument(
        "odom_frame",
        default_value="odom",
        description="Odom frame for relocalization output map->odom.",
    )
    declare_base_frame = DeclareLaunchArgument(
        "base_frame",
        default_value="base_footprint",
        description="Base frame used for base->lidar extrinsic lookup.",
    )
    declare_robot_base_frame = DeclareLaunchArgument(
        "robot_base_frame",
        default_value="gimbal_yaw",
        description="Robot base frame used when applying /initialpose.",
    )
    declare_lidar_frame = DeclareLaunchArgument(
        "lidar_frame",
        default_value="front_mid360",
        description="Lidar frame name.",
    )

    livox_simulation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_livox_sim_dir, "launch", "livox_simulation.launch.py")
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "world": sim_world,
            "x": sim_x,
            "y": sim_y,
            "z": sim_z,
            "yaw": sim_yaw,
        }.items(),
    )

    point_lio_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_point_lio_dir, "launch", "point_lio.launch.py")
        ),
        launch_arguments={
            "namespace": "",
            "rviz": "False",
            "point_lio_cfg_dir": point_lio_cfg_dir,
        }.items(),
    )

    relocalization_node = Node(
        package="small_gicp_relocalization",
        executable="small_gicp_relocalization_node",
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

    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_dir, "launch", "navigation2.launch.py")
        ),
        condition=IfCondition(launch_nav2),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "map": map_yaml,
            "params_file": nav2_params_file,
        }.items(),
    )

    return LaunchDescription(
        [
            declare_use_sim_time,
            declare_sim_x,
            declare_sim_y,
            declare_sim_z,
            declare_sim_yaw,
            declare_world,
            declare_point_lio_cfg,
            declare_map_yaml,
            declare_nav2_params,
            declare_launch_nav2,
            declare_launch_relocalization,
            declare_prior_pcd_file,
            declare_registered_scan_topic,
            declare_map_frame,
            declare_odom_frame,
            declare_base_frame,
            declare_robot_base_frame,
            declare_lidar_frame,
            livox_simulation_launch,
            point_lio_launch,
            relocalization_node,
            nav2_launch,
        ]
    )
