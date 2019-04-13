#!/bin/sh
cd parkslab
rm -d -r migrations/
cd ..
rm -d -r db.sqlite3
python manage.py makemigrations manager
python manage.py migrate
python manage.py createsuperuser