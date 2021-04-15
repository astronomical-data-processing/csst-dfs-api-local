# CSST local APIs library

## Introduction

This package provides APIs to access csst's files and databases in your localized environment.

## Installation

This library can be installed with the following command: 

```bash
git clone https://github.com/astronomical-data-processing/csst-dfs-api-local.git
cd csst-dfs-api-local
pip install -r requirements.txt
python setup.py install
```

## Configuration
set enviroment variable
    CSST_LOCAL_FILE_ROOT = [a local file directory] #default: /opt/temp/csst
