import os
import setuptools

requirements = []
path = os.path.dirname(os.path.realpath(__file__)) + '/requirements.txt'
if os.path.isfile(path):
    try:
        with open(path) as f:
            requirements = f.read().split()
    except Exception as ex:
        print(ex)

setuptools.setup(
    name='plag-cli',
    version='1.0',
    author='divyansh',
    description='A CLI application to detect plagiarism in source code files.',
    packages=setuptools.find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'plag = package.__main__:start',
        ]
    }
)
