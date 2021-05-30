from sys import version
from setuptools import setup

setup(
    name='plag-cli',
    version='0.1',
    packages=['package'],
    entry_points={
        'console_scripts': [
            'plag = package.__main__'
        ]
    }
)
