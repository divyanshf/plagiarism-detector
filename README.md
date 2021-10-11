# Plag

## Description
A CLI Application to detect plagiarism in **Source Code Files**.


## Features
- Compare source code files for plagiarism.
- Extract code features from a file.
- Language support for C++ and Java.
- Cross-platform compatibilty.
- User customizability.

## Technologies / Libraries Used
- [Python](https://www.python.org/)
- [Numpy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Typer](https://typer.tiangolo.com/)
- [NLTK](https://www.nltk.org/)
- [CppHeaderParser](https://pypi.org/project/CppHeaderParser/)
- [PlyJ](https://github.com/musiKk/plyj)

## Prerequisites
- [Python](https://www.python.org/) (version >= 3.0)

## Installation
- Clone this repository.
- Change the current directory to the repository
  ```
  cd <path_to_repository>
  ```
- Install the python package
  ```
  python setup.py install
  ```

## Usage
- Check the version of Plag.
  ```
  plag --version
  ```
- Comparing Source Code Files for similarity.
  ```
  plag compare ../data/file1.cpp ../data --filetype cpp 
  ```
- Extracting features of a Source Code file.
  ```
  plag extract ../data/file1.cpp
  ```
- Show current preferences
  ```
  plag preference show
  ```
- Set a preference.
  ```
  plag preference set filetype py
  ```
- Reset all preferences
  ```
  plag preference reset
  ```
*NOTE* : The preferences currently supported are
  - filetype
  - threshold
  - result_path
  - comment_weight

## Common Issues
- In case of permission errors, try running the application as administrator.
