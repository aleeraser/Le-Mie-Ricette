#!/bin/bash

PORT=5000

function usage {
	echo
	echo "Usage:"
	echo "  - server [-h, --help] : print this help menu"
	echo "  - server setup        : setup virtualenv and pip packages"
	echo "  - server (re)start    : (re)start server"
	echo "  - server stop         : stop server"
    echo "  - server debug        : start server in debug mode"
    echo
	echo "Note: the server starts on localhost:$PORT."
}

function err {
	echo $1
    usage
	exit 1
}

function venv_activate {
    source ./flaskenv/bin/activate
}

function assert_server_not_running {
    if [ -f "./le_mie_ricette.pid" ]; then
        echo "Server is already running."
        exit 0
    fi
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
    mkdir -p "./img/uploaded"
    mkdir -p "./img/uploaded/ingredienti"
    mkdir -p "./img/uploaded/ricette"
    mkdir -p "./img/uploaded/preparazioni"
    mkdir -p "./pdf"
    mkdir -p "./pdf/menu"
    mkdir -p "./pdf/ricette"
    mkdir -p "./pdf/preparazioni"
}

if [ $# -ge "2" ]; then
    err "Wrong number of parameters."
else
    # perform setup if flaskenv folder is not found
    [ -d "./flaskenv" ] || setup

    if [ "$1" == "setup" ]; then
        setup
    elif [ "$1" == "start" ]; then
        assert_server_not_running
        venv_activate && gunicorn app:app -b 0.0.0.0:$PORT -p "le_mie_ricette.pid" -D && echo "Server started"
    elif [ "$1" == "restart" ]; then
        venv_activate
        kill -HUP `cat le_mie_ricette.pid &>/dev/null` &>/dev/null
        if [ ! -f "le_mie_ricette.pid" ]; then
            gunicorn app:app -b 0.0.0.0:$PORT -p "le_mie_ricette.pid" -D && echo "No server was running. Server started."
        else
            echo "Server restarted"
        fi
    elif [ "$1" == "stop" ]; then
        if [ ! -f "./le_mie_ricette.pid" ]; then
            echo "Server was not running."
            exit 0
        else
            kill `cat ./le_mie_ricette.pid` &>/dev/null || rm "./le_mie_ricette.pid"
            echo "Server stopped"
        fi
    elif [ "$1" == "debug" ]; then
        assert_server_not_running
        venv_activate && gunicorn app:app -b 0.0.0.0:$PORT
    elif [ $# != 0 ]; then
        err "Wrong parameter."
    fi
fi