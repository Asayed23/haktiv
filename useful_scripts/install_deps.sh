# tested on Ubuntu 18.04.3 LTS
sudo apt-get update

# python 
sudo apt-get install python3.7 python3.7-dev -y
sudo apt-get install python3-pip -y
sudo apt-get install virtualenv -y
sudo apt-get install python3-psycopg2 -y

# other libs
sudo apt-get install libpq-dev -y
sudo apt-get install -y libxml2-dev libxslt1-dev

# database 
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
RELEASE=$(lsb_release -cs)
echo "deb http://apt.postgresql.org/pub/repos/apt/ ${RELEASE}"-pgdg main | sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update
sudo apt -y install postgresql-11
sudo apt-get install postgresql-server-dev-all -y

sudo apt-get install redis -y

curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add

sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'

sudo apt-get install pgadmin4 -y

sudo apt-get install pgadmin4-web -y

sudo /usr/pgadmin4/bin/setup-web.sh

virtualenv -p python3 ../env