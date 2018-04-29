#!/bin/bash

function usage {
	echo
	echo "Usage:"
	echo "  - server [-h, --help] : print this help menu"
	echo "  - server setup        : setup virtualenv and pip packages"
	echo "  - server (re)start    : (re)start server"
	echo "  - server stop         : stop server"
    echo "  - server debug        : start server in debug mode"
    echo
	echo "Note: the server starts on localhost:5001."
}

function err {
	echo $1
    usage
	exit 1
}

function venv_activate {
    source ./flaskenv/bin/activate
}

function setup {
    echo
    echo "WARNING: pre-requisites are a working version of"
    echo "Python 2.7 and having virtualenv installed."
    echo
    echo "If you meet the requirements, press any key to continue."
    echo "Otherwise, CTRL-C now."

    # Press any key to continue
    read -n 1 -s -r

    # virtualenv flaskenv && venv_activate && pip install setuptools --upgrade && pip install Flask flask-mysqldb gunicorn Flask-WeasyPrint cairocffi cairosvg==1.0.22
    virtualenv flaskenv && venv_activate && pip install setuptools --upgrade && pip install -r requirements.txt

    cd "./static/"
    mkdir "./img/uploaded"
    mkdir "./img/uploaded/ingredienti"
    mkdir "./img/uploaded/ricette"
    mkdir "./img/uploaded/preparazioni"
    mkdir "./pdf"
    mkdir "./pdf/menu"
    mkdir "./pdf/ricette"
    mkdir "./pdf/preparazioni"
}

if [ $# -ge "2" ]; then
    err "Wrong number of parameters."
else
    # perform setup if flaskenv folder is not found
    [ -d "./flaskenv" ] || setup

    if [ "$1" == "start" ]; then
        setup
    elif [ "$1" == "start" ]; then
        venv_activate && gunicorn app:app -b 0.0.0.0:5001 -p "le_mie_ricette.pid" -D && echo "Server started"
    elif [ "$1" == "restart" ]; then
        venv_activate && kill -HUP `cat le_mie_ricette.pid` && echo "Server restarted"
    elif [ "$1" == "stop" ]; then
        if [ ! -f "./le_mie_ricette.pid" ]; then
            echo "Server was not running."
            exit 0
        fi
        venv_activate && kill `cat ./le_mie_ricette.pid` && echo "Server stopped"
    elif [ "$1" == "debug" ]; then
        venv_activate && gunicorn app:app -b 0.0.0.0:5001
    elif [ $# != 0 ]; then
        err "Wrong parameter."
    fi
fi