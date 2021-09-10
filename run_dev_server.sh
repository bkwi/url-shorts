#!/bin/sh

export PYTHONDONTWRITEBYTECODE=TRUE
export PYTHONUNBUFFERED=TRUE

exec adev runserver shorts/app.py --app-factory create_app
