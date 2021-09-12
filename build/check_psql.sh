#!/bin/sh

until pg_isready -h $POSTGRES_HOST -p 5432 -U postgres
do
  echo "Waiting for postgres. Host: $POSTGRES_HOST"
  sleep 2;
done
