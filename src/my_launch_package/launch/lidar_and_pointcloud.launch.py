import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import launch

################### user configure parameters for ros2 start ###################
xfer_format   = 1    # 0-Pointcloud2(PointXYZRTL), 1-customized pointcloud format
multi_topic   = 0    # 0-All LiDARs share the same topic, 1-One LiDAR one topic
data_src      = 0    # 0-lidar, others-Invalid data src
publish_freq  = 10.0 # frequency of publish, 5.0, 10.0, 20.0, 50.0, etc.
output_type   = 0
frame_id      = 'livox_frame'
lvx_file_path = '/home/livox/livox_test.lvx'
cmdline_bd_code = 'livox0000000001'

# Assume the 'config' directory is located within the 'launch' directory
# Construct the correct paths to the config and RViz files
cur_path = os.path.dirname(os.path.realpath(__file__)) + '/../'
cur_config_path = os.path.join(cur_path, 'config')
rviz_config_path = os.path.join(cur_config_path, 'display_point_cloud_ROS2.rviz')
user_config_path = os.path.join(cur_config_path, 'MID360_config.json')
################### user configure parameters for ros2 end #####################

# Parameters to be passed to the livox_ros_driver2 node
livox_ros2_params = [
    {"xfer_format": xfer_format},
    {"multi_topic": multi_topic},
    {"data_src": data_src},
    {"publish_freq": publish_freq},
    {"output_data_type": output_type},
    {"frame_id": frame_id},
    {"lvx_file_path": lvx_file_path},
    {"user_config_path": user_config_path},
    {"cmdline_input_bd_code": cmdline_bd_code}
]

def generate_launch_description():
    static_transform_publisher_map = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_map_odom',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom']
    )
    
    static_transform_publisher_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_odom_base',
        arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_link']
    )
    
    static_transform_publisher_lidar = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_base_lidar',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'livox_frame']
    )


    # Define the livox driver node with parameters
    livox_driver = Node(
        package='livox_ros_driver2',
        executable='livox_ros_driver2_node',
        name='livox_lidar_publisher',
        output='screen',
        parameters=livox_ros2_params  # Pass the configuration parameters to the node
    )

    # Define the RViz node
    livox_rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        #arguments=['--display-config', rviz_config_path]  # Load the RViz config file
    )

    livox_to_pcl2_node = Node(
        package='livox_to_pointcloud2',
        executable='livox_to_pointcloud2_node',
        name='livox_to_pcl2',
        output='screen',
        remappings=[
            ('/livox2/lidar','/livox/lidar'),
            ('/livox/points','/livox/cloud_lidar'),
        ],
    )
    
    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan', 
        executable='pointcloud_to_laserscan_node',
        remappings=[
            ('cloud_in', '/livox/cloud_lidar'),
            ('scan', '/scan'),
        ],
        parameters=[{
            'target_frame': 'livox_frame',
            'transform_tolerance': 0.01,
            'min_height': 0.0,
            'max_height': 1.0,
            'angle_min': -1.5708,  # -M_PI/2
            'angle_max': 1.5708,  # M_PI/2
            'angle_increment': 0.0087,  # M_PI/360.0
            'scan_time': 0.3333,
            'range_min': 0.45,
            'range_max': 15.0,
            'use_inf': True,
            'inf_epsilon': 1.0
        }],
        name='pcl_to_ls',
    )


    return LaunchDescription([
        static_transform_publisher_map,
        static_transform_publisher_odom,
        static_transform_publisher_lidar,
        livox_driver,
        livox_rviz,
        livox_to_pcl2_node,
	pointcloud_to_laserscan_node
    ])
