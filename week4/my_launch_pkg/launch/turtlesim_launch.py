from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction, ExecuteProcess

def generate_launch_description():
    return LaunchDescription([

        # Turtle simulator
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='sim'
        ),

        # Keyboard control (xterm)
        Node(
            package='turtlesim',
            executable='turtle_teleop_key',
            name='teleop',
            prefix='xterm -e'
        ),

        # Spawn turtle2
        TimerAction(
            period=2.0,
            actions=[
                ExecuteProcess(
                    cmd=[
                        'ros2', 'service', 'call',
                        '/spawn',
                        'turtlesim/srv/Spawn',
                        "{x: 5.0, y: 5.0, theta: 0.0, name: 'turtle2'}"
                    ],
                    output='screen'
                )
            ]
        )
    ])
