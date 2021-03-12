#Script to start quick dev database 

DB_SYS_USER='postgres'
DB_NAME='middlebeasts_db'
DB_USERNAME='middlebeasts'
DB_PASSWORD='AukKJhMzJ2vq2sSE'

if  ! id -u $DB_SYS_USER > /dev/null 2>&1; then
    psqlcc='psql postgres'
    else
    psqlcc='sudo -u postgres psql'
fi

echo "New Database " "$DB_NAME"
    $psqlcc -c "DROP DATABASE $DB_NAME;" > /dev/null 2>&1
    $psqlcc -c "CREATE DATABASE $DB_NAME;" > /dev/null 2>&1
echo "New Database User " "$DB_USERNAME"
    $psqlcc -c "DROP USER $DB_USERNAME;" > /dev/null 2>&1
    $psqlcc -c "CREATE USER $DB_USERNAME WITH ENCRYPTED PASSWORD '$DB_PASSWORD';" > /dev/null 2>&1
echo "GRANT ALL PRIVILEGES" "$DB_USERNAME" "$DB_NAME"
    $psqlcc -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USERNAME;" > /dev/null 2>&1

echo "DB USER $DB_USERNAME"
echo "DB PASSWORD $DB_PASSWORD"
echo "DB NAME $DB_NAME"