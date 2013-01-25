fec-standardizer
================

An experiment to standardize individual donor names in federal campaign finance data using simple graph theory and machine learning.

## Basics

BLAH

## Setting up and running the workflow

FIRST INSTALL

```
pip install numpy
pip install -r requirements.txt
python manage.py syncdb
```

NEXT ENV VARS

```
export PYTHONPATH=/wherever/you/clone/project:/wherever/you/clone/project/campfin
export DJANGO_SETTINGS_MODULE=campfin.settings
```

NEXT IMPORT DATA:

```
cd campfin/bin
python import.py
```