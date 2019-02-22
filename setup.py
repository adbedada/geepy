from setuptools import find_packages, setup

REQUIRED = [
    'click>=7.0',
    'fiona>=1.8.4',
    'shapely>=1.6.4',
    'rasterio>=1.0.18'
]
setup(
    name='geepy',
    version=0.1,
    entry_points='''
        [console_scripts]
        geepy=geepy.cli:commands
        ''',
    packages=find_packages(),
    install_requires=REQUIRED
)