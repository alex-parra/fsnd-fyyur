#! bin/bash

PG_PASS="PGPASSWORD=123456"
PG_CONN="$PG_PASS psql -h pg -U postgres"
DB_NAME="fyyur"

initDb() {
  docker-compose run pg bash -c "$PG_CONN -tc \"SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'\" | grep -q 1 || $PG_CONN -c \"CREATE DATABASE $DB_NAME\""
  flask db upgrade
}

dropDb() {
  docker-compose run pg bash -c "$PG_PASS dropdb -h pg -U postgres $DB_NAME"
}

case $1 in
  db-init) initDb ;;
  db-drop) dropDb ;;
  dev) FLASK_APP=app FLASK_ENV=development flask run ;;
  *) echo 'Unknown mode. Try sh boot.sh dev' ;;
esac