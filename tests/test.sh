#!/bin/bash

export PG_HOST=127.0.0.1
export PG_PORT=5432
export PG_USER=test
export PG_PASSWORD=test
export PG_DBNAME=postgres
export SECRET_KEY="django-insecure-#i74xbav1g6_0l9i!e=)nojr34oh65kzw+yf%_6_n=dqc8q9v3"
python3 manage.py test $1
