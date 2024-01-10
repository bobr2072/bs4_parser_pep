# Parsing of PEP with Beautiful Soup

## Stack

[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=ffffff&color=043A6B)](https://www.python.org/)
[![BeautifulSoup4](https://img.shields.io/badge/-BeautifulSoup4-464646?style=flat&logo=BeautifulSoup4&logoColor=ffffff&color=043A6B)](https://www.crummy.com/software/BeautifulSoup/)
[![Prettytable](https://img.shields.io/badge/-Prettytable-464646?style=flat&logo=Prettytable&logoColor=ffffff&color=043A6B)](https://github.com/jazzband/prettytable)
[![Logging](https://img.shields.io/badge/-Logging-464646?style=flat&logo=Logging&logoColor=ffffff&color=043A6B)](https://docs.python.org/3/library/logging.html)

## Description

The parser collects data about all PEP documents, compares statuses and writes them to a file,
collection of information about the status of versions, downloading an archive with documentation and collecting links about news in Python are also implemented,
logs its work and errors to the command line and a log file.

## Documentation

Usage: 
```
main.py [-h] [-c] {pep,whats-new,latest-versions,download} [-o {pretty,file}]
```

Required Arguments:
```
  {pep,whats-new,latest-versions,download}    Parser operating modes
```

Optional Arguments:
```
  -h, --help            Show documentation
  -c, --clear-cache     Clearing cache
  -o {pretty,file}, --output {pretty,file}    Additional data output methods
```

## Author

Boris Korenblias
