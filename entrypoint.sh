#!/bin/sh
python manage.py wait_for_db
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py add_superuser 