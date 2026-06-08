from setuptools import find_packages, setup

package_name = 'lab7_pkg'

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
    maintainer='muteebajaved',
    maintainer_email='muteebajaved5@gmail.com',
    description='Lab Manual 7 – Autonomous Navigation with Nav2 and Multi-Waypoint Mission Planning',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            # Task 2: Hardcoded 5-waypoint mission navigator
            'waypoint_navigator = lab7_pkg.waypoint_navigator:main',
            # Task 3: Dynamic waypoint injection via CLI arguments
            'waypoint_navigator_dynamic = lab7_pkg.waypoint_navigator_dynamic:main',
            # Map post-processing utility (run once after SLAM)
            'fix_map = lab7_pkg.fix_map:main',
        ],
    },
)
