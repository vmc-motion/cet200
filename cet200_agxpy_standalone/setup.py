# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# For ros2 execution
from glob import glob
from setuptools import setup, find_packages

package_name = 'cet200_agxpy_standalone'

setup(
    name=package_name,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', '../LICENSE', '../NOTICE']),
        ('lib/agx_file', glob('../agx_file/*')),
    ],
    entry_points={
        'console_scripts': [
            'cet200_on_ground = cet200_agxpy_standalone.apps.cet200_on_ground:main',
            'cet200_on_terrain = cet200_agxpy_standalone.apps.cet200_on_terrain:main',
            'cet200_compare_models = cet200_agxpy_standalone.apps.cet200_compare_models:main',
        ],
    },
)
