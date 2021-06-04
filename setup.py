from sys import version
from setuptools import setup
import setuptools

setup(
    name='plag-cli',
    version='0.1',
    author='divyansh',
    description='A CLI application to detect plagiarism in source code files.',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'plag = package.__main__:main'
        ]
    }
)
