from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'isaac'

def package_files(directory):
    """Collect all files under a given directory."""
    paths = []
    for (path, _, filenames) in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(path, filename)
            install_path = os.path.join('share', package_name, os.path.relpath(path, '.'))
            paths.append((install_path, [file_path]))
    return paths

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ]
    + package_files('launch')
    + package_files('config'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='labor',
    maintainer_email='labor@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
