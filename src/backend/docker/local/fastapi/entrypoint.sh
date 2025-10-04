#!/bin/bash

set -o errexit

set -o nounset

set -o pipefail

python << END

import sys
import time
import psycopg

MAX_WAIT_SECONDS = 30
RETRY_INTERVAL_SECONDS = 5
start_time = time.time()

def check_database():
    try:
        psycopg.connect(
            dbname="${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password="${POSTGRES_PASSWORD}",
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}"
        )
        return True
    except psycopg.OperationalError as err:
        elapsed = int(time.time() - start_time)
        sys.stderr.write(f"Database connection failed ({elapsed} seconds elapsed): {err}\n")
        return False    

while True:
    if check_database():
        break
    if time.time() - start_time > MAX_WAIT_SECONDS:
        sys.stderr.write("Exceeded maximum wait time for database connection. Exiting.\n")
        sys.exit(1)

    sys.stderr.write(f"Retrying in {RETRY_INTERVAL_SECONDS} seconds...\n")
    time.sleep(RETRY_INTERVAL_SECONDS)
END

echo >&2 "Postgres is up - and ready  to accept connections"

exec "$@"