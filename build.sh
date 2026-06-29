#!/usr/bin/env bash
set -o errexit

pip install -r backend/requirements.txt

mkdir -p logs ml_models

cd backend
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_users
