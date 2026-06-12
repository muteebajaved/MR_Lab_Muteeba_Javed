from setuptools import find_packages, setup

package_name = 'camera_follower'

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
    maintainer='Muteebajaved',
    maintainer_email='muteebajaved5@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
    'console_scripts': [
        'camera_follower = camera_follower.camera_follower:main',
        'clr_follower = camera_follower.clr_follower:main',
        'tracking = camera_follower.tracking:main',
    ],
},
     )
