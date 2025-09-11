#!/bin/bash
sudo apt update && sudo apt install postgresql postgresql-contrib -y

# FUTURE
# all postgresql default to localhost 5432 (it is one postgres instance one localhost:5432 - can use initdb to create others on new ip:port)
# remove hostname and port for 1.0 -- can add a more in depth script if need to spin up many postgres instances and specify whether
# The main config files which we can edit automatically are /etc/postgresql/<int>/main/<postgresl.conf / pg_hba.conf>

DB_USER=user
DB_PASSWORD=pwd
DB_NAME=db_name

# postgresql creating a new db requires sudo permissions - we will send the file over to them and just have the end user run it
systemctl start postgresql
# create the given user/password; create db with it as owner; grant user all privileges to DB
sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
echo "Database created! Connect using: "psql -U $DB_USER -d $DB_NAME -h localhost -p 5432""