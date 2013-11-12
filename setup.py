from setuptools import setup, find_packages
from  distutils.sysconfig import get_python_version

packages = find_packages(exclude=['tests'])
MINIMAL_PYTHON_VERSION = '2.7'
if get_python_version() < MINIMAL_PYTHON_VERSION:
    raise Exception('requires python >=%s of python (for OrderedDict support)' % MINIMAL_PYTHON_VERSION)

setup(
    name = "magritte",
    version = "0.4",
    packages = packages,
    author = "NFB/ONF",
    author_email = "m.lavallee@onf.ca",
    description = "Collection of utilities to maintain a local pypi server",
    url = 'https://github.com/mlavallee/magritte.git',
    install_requires=['pip>=1.0', 'simplejson>=2.1.0'],
    entry_points={
        'console_scripts': [
            'magritte = magritte.main:main',
        ]
    },
)
