from setuptools import find_packages, setup

package_name = 'my_turtle_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='muteeba',
    maintainer_email='muteeba@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'circle = my_turtle_package.circle:main',
        'triangle = my_turtle_package.triangle:main',
        'multi = my_turtle_package.multi_turtle:main',
        'goal = my_turtle_package.go_to_goal:main',
    ],
},
)
