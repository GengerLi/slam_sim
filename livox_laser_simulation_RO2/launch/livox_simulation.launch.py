import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node

def generate_launch_description():

    package_name = 'ros2_livox_simulation'
    robot_name = 'my_robot'
    
    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')
    x_pose = LaunchConfiguration('x')
    y_pose = LaunchConfiguration('y')
    z_pose = LaunchConfiguration('z')
    yaw_pose = LaunchConfiguration('yaw')

    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    pkg_ros2_livox_simulation = get_package_share_directory(package_name)
    package_models_path = os.path.join(pkg_ros2_livox_simulation, 'resourse', 'models')
    system_models_path = '/usr/share/gazebo-11/models'

    world_path = [
        os.path.join(pkg_ros2_livox_simulation, 'resourse', 'worlds', ''),
        world,
        '.world'
    ]


    model_paths = [package_models_path, system_models_path]
    existing_model_path = os.environ.get('GAZEBO_MODEL_PATH', '')
    if existing_model_path:
        model_paths.insert(0, existing_model_path)
    os.environ['GAZEBO_MODEL_PATH'] = os.pathsep.join(model_paths)
    resource_paths = [pkg_ros2_livox_simulation, '/usr/share/gazebo-11', '/usr/share/gazebo-11/media']
    existing_resource_path = os.environ.get('GAZEBO_RESOURCE_PATH', '')
    if existing_resource_path:
        resource_paths.insert(0, existing_resource_path)
    os.environ['GAZEBO_RESOURCE_PATH'] = os.pathsep.join(resource_paths)


    declare_use_sim_time = DeclareLaunchArgument('use_sim_time', default_value='true')
    declare_world_cmd = DeclareLaunchArgument('world',default_value='RC26_zhangai')
    declare_x_cmd = DeclareLaunchArgument('x', default_value='0')
    declare_y_cmd = DeclareLaunchArgument('y', default_value='0.0')
    declare_z_cmd = DeclareLaunchArgument('z', default_value='0.1')
    declare_yaw_cmd = DeclareLaunchArgument('yaw', default_value='1.57')

    gazebo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            'world': world_path,
            'gui': 'true',
            'verbose': 'true'
        }.items()
    )


    xacro_file = os.path.join(pkg_ros2_livox_simulation, 'urdf', robot_name, robot_name + '.xacro')
    robot_description = Command([f'xacro {xacro_file}'])
    
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description},
            {'use_sim_time': use_sim_time}
        ],
    )


    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'my_robot',
            '-topic', 'robot_description',
            '-x', x_pose,
            '-y', y_pose,
            '-z', z_pose,
            '-Y', yaw_pose
        ],
        output='screen'
    )



    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "myrobot_joint_state_broadcaster",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "120",
        ],
        output="screen",
    )

    diff_drive_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "diff_drive_controller",
            "--controller-manager", "/controller_manager",
            "--controller-manager-timeout", "120",
        ],
        output="screen",
    )

    start_joint_state_after_spawn = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_state_broadcaster_spawner],
        )
    )

    start_diff_drive_after_joint_state = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[diff_drive_controller_spawner],
        )
    )


    bringup_pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        remappings=[
            ('cloud_in', '/livox/lidar/pointcloud'),
            ('scan', '/scan')
        ],
        parameters=[
            {
                'target_frame': 'base_link',
                'transform_tolerance': 0.01,
                'min_height': -1.0,
                'max_height': 0.1,
                'angle_min': -3.14159,
                'angle_max': 3.14159,
                'angle_increment': 0.0043,
                'scan_time': 0.3333,
                'range_min': 0.45,
                'range_max': 10.0,
                'use_inf': True,
                'inf_epsilon': 1.0
            },
            {'use_sim_time': use_sim_time},
        ],
        name='pointcloud_to_laserscan'
    )
    start_pointcloud_after_diff_drive = RegisterEventHandler(
        OnProcessExit(
            target_action=diff_drive_controller_spawner,
            on_exit=[bringup_pointcloud_to_laserscan_node],
        )
    )

    # ====================== LaunchDescription ======================
    ld = LaunchDescription()

    ld.add_action(declare_use_sim_time)
    ld.add_action(declare_world_cmd)
    ld.add_action(declare_x_cmd)
    ld.add_action(declare_y_cmd)
    ld.add_action(declare_z_cmd)
    ld.add_action(declare_yaw_cmd)

    ld.add_action(gazebo_launch)
    ld.add_action(robot_state_publisher)
    ld.add_action(spawn_entity)

    ld.add_action(start_joint_state_after_spawn)
    ld.add_action(start_diff_drive_after_joint_state)

    ld.add_action(start_pointcloud_after_diff_drive)

    return ld
