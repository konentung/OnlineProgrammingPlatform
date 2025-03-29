#!/bin/bash

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput
