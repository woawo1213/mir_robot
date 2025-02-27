import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, \
    SetLaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    mir_gazebo_dir = get_package_share_directory('mir_gazebo')
    mir_nav_dir = get_package_share_directory('mir_navigation')

    def find_map_file(context):
        map_arg = context.launch_configurations['map']
        if(os.path.isfile(os.path.join(mir_nav_dir, 'maps', map_arg))):
            return[SetLaunchConfiguration('map_file', os.path.join(mir_nav_dir, 'maps', map_arg))]
        elif (os.path.isfile(map_arg)):
            return[SetLaunchConfiguration('map_file', map_arg)]

    declare_namespace_arg = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Namespace to push all topics into.')

    declare_world_argument = DeclareLaunchArgument(
        'world',
        default_value='maze',
        description='Choose simulation world. Available worlds: empty, maze')

    declare_map_file_argument = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(mir_nav_dir, 'maps', 'maze.yaml'),
        description='Relative path to map in mir_navigation/maps or full path to map (yaml).')

    declare_rviz_config_file_argument = DeclareLaunchArgument(
        'rviz_config_file',
        default_value=os.path.join(mir_nav_dir, 'rviz', 'mir_nav.rviz'),
        description='Full path to rviz configuration file')

    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation/Gazebo clock')

    declare_slam_params_file_cmd = DeclareLaunchArgument(
        'slam_params_file',
        default_value=os.path.join(get_package_share_directory("mir_navigation"),
                                   'config', 'mir_mapping_async_sim.yaml'),
        description='Full path to the ROS2 parameters file to use for the slam_toolbox node')

    launch_simulation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(mir_gazebo_dir, 'launch', 'mir_gazebo_launch.py')),
        launch_arguments={'rviz_config_file': LaunchConfiguration(
            'rviz_config_file')}.items()
    )

    launch_amcl = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(mir_nav_dir, 'launch', 'include', 'amcl.py')),
        launch_arguments={'map': LaunchConfiguration('map_file')}.items()
    )

    launch_navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(mir_nav_dir, 'launch', 'include', 'navigation.py')),
        launch_arguments={'map_subscribe_transient_local': 'true'}.items()
    )

    ld = LaunchDescription()

    ld.add_action(declare_namespace_arg)
    ld.add_action(declare_world_argument)
    ld.add_action(declare_map_file_argument)
    ld.add_action(declare_use_sim_time_argument)
    ld.add_action(declare_slam_params_file_cmd)
    ld.add_action(declare_rviz_config_file_argument)
    ld.add_action(OpaqueFunction(function=find_map_file))

    ld.add_action(launch_simulation)
    ld.add_action(launch_amcl)
    ld.add_action(launch_navigation)

    return ld
