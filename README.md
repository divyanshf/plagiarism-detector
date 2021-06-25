# Plag
A CLI Application to detect plagiarism in Source Code Files.

## Prerequisites
- [Python >= v3.0](https://www.python.org/)

## Installation
- Clone this repository.
- Run the following in the terminal.
```
cd <path_to_repository>
python setup.py install
```
This will install the package on your local system.

## Commands
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
- Handling user preferences
  - Show current preferences
  ```
  plag preference show
  ```
  - Set a preference
  ```
  plag preference set filetype py
  ```
  - Reset all preferences
  ```
  plag preference reset
  ```
