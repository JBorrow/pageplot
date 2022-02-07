#!bash

isort setup.py
black setup.py

isort tests
black tests

isort pageplot --skip __init__.py
black pageplot
