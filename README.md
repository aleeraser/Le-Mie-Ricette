# ![QR-Vey](static/img/logo2.png?raw=true "QR-Vey")

## Le Mie Ricette

A simple platform for managing recipes, ingredients and menus.

### Pre-requisites

- python 2.7 (usually pre-installed)
- homebrew (only if installing on Mac):
  - `$ /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`
- pip 2.7:
  - `$ sudo easy_install [--upgrade] pip`
- virtualenv:
  - `$ [sudo -H] pip install virtualenv`
- mysql
  - on Mac:
    - `$ brew install mysql`
    - set mysql root password:
      - `$ mysqladmin -u root password 'password'`
    - use brew services to start/stop mysql
      - `$ brew tap homebrew/services`
      - `$ brew services start mysql`
  - on Linux:
    - `$ sudo apt-get install mysql-server mysql-client libmysqlclient-dev`
    - `$ mysql_secure_installation`

Some dependencies are needed:

- on Linux:
  - `$ sudo apt-get install libxml2-dev libxslt-dev libffi-dev libcairo2-dev libpango1.0-dev`
- on Mac:
  - `$ brew install cairo pango gdk-pixbuf libffi`

### Starting the server

`$ ./server.sh start`

If ran for the first time, this will trigger an initial setup. equivalent of running `$ ./server.sh setup` and `$ ./server.sh start`.
