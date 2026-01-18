#! /usr/bin/env bash

# Let the DB start
python -c "import sys; print('Waiting for database connection...');"

# Run migrations
alembic upgrade head
