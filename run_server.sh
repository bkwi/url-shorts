#!/bin/sh

# export PYTHONDONTWRITEBYTECODE=TRUE
export PYTHONUNBUFFERED=TRUE

./build/check_psql.sh

exec python shorts/app.py
