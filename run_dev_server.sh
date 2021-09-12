#!/bin/sh

export PYTHONDONTWRITEBYTECODE=TRUE
export PYTHONUNBUFFERED=TRUE

./build/check_psql.sh

exec adev runserver shorts/app.py --app-factory create_app
