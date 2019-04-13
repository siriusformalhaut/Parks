#!/bin/sh
python3 manage.py makemigrations manager
python3 manage.py migrate
