#!/usr/bin/env bash

# Check for correct python version

# Runs the python version command and gets the number (2nd field), needs the `` characters which tell it that is a whole command
VERSION=`python3 --version | awk '{print $2}'`

# Starts at 0th index character and goes up by 1. Then for next two, start at 2nd index character and go up by 1. 
if [ "${VERSION:0:1}" -ne "3" ] || [ "${VERSION:2:1}" -lt "7" ] || [ "${VERSION:2:1}" -gt "10" ]
then
	echo "You must use Python 3.7 - 3.10. You are using $VERSION"
    echo "When upgrading, remember to install python3.X-dev and python3.X-venv (and maybe the right pip)"
	return 1
else
	echo -e "You are using Python $VERSION"
fi

# Create a virtual environment for dependencies
if [ ! -d venv ]
then
  python3 -m venv venv
fi
# The . is the same thing as 'source'
. venv/bin/activate

# upgrade pip
python3 -m pip install --upgrade pip #added python-m for pip installs (source setup overwrite for venv)

# install requirements
python3 -m pip install -r requirements.txt
# To generate a new requirements.txt file, run "pip freeze > requirements.txt"


# Export any environment variables
