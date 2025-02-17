#!/bin/bash

# Database configuration
DB_USER="newuser"
DB_PASSWORD="new_password"  # Replace with your database password
DB_NAME="moodle_db"
SQL_FILE_PATH="./moodle.sql"
PYTHON_FILE_PATH="./moodleCron.py"

# Step 1: Check if MariaDB is running
if ! pgrep -x "mysqld" > /dev/null; then
    echo "MariaDB is not running. Starting MariaDB..."
    if sudo systemctl start mariadb; then
        echo "MariaDB started successfully."
    else
        echo "Failed to start MariaDB."
        exit 1
    fi
fi

# Step 2: Create the database if it doesn't exist
echo "Creating database if not exists..."
mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;" || {
    echo "Failed to create database $DB_NAME."
    exit 1
}

# Step 3: Import SQL file into the database
if [ -f "$SQL_FILE_PATH" ]; then
    echo "Importing data from $SQL_FILE_PATH..."
    mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$SQL_FILE_PATH" || {
        echo "Failed to import SQL data from $SQL_FILE_PATH."
        exit 1
    }
else
    echo "SQL file $SQL_FILE_PATH not found!"
    exit 1
fi

# Step 4: Execute moodleCron.py to fetch the LA events, quiz and assignment grades
if [ -f "$PYTHON_FILE_PATH" ]; then
    echo "Fetching daily LA-events..."
    python3 "$PYTHON_FILE_PATH" || {
        echo "Python script $PYTHON_FILE_PATH failed."
        exit 1
    }
else
    echo "Python file $PYTHON_FILE_PATH not found!"
    exit 1
fi

echo "Setup complete."
