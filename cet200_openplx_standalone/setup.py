# Copyright VMC Motion Technologies Co., Ltd.
# Licensed under the Apache-2.0 license. See LICENSE.

# For ros2 execution
from glob import glob
from setuptools import setup, find_packages

package_name = 'cet200_openplx_standalone'

setup(
    name=package_name,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml', '../LICENSE', '../NOTICE']),
        ('lib/agx_file', glob('../agx_file/*')),
        ('lib/openplx', glob('../openplx/*')),
    ],
    entry_points={
        'console_scripts': [
            'cet200_on_ground = cet200_openplx_standalone.cet200:main',
        ],
    },
)
