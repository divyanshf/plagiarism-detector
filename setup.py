from sys import version
from setuptools import setup

setup(
    name='plag-cli',
    version='0.1',
    author='divyansh',
    description='A CLI application to detect plagiarism in source code files.',
    packages=['package', 'package.helper'],
    entry_points={
        'console_scripts': [
            'plag = package.main:main'
        ]
    }
)
