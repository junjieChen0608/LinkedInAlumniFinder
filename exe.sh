#!/usr/bin/env bash
# Highlighting
bold=$(tput bold)
normal=$(tput sgr0)
echo "Please make sure ${bold}\"crawler.py\"${normal} contains the following:"
echo "- path to ${bold}\"chromedriver\"${normal} executable"
echo "- correct ${bold}\"credentials\"${normal} for crawling account"
# Recommended to use "virtualenv" and "virtualenvwrapper" for Python3!
pip3 install -r requirements.txt  # installs all necessary python packages listed in "requirements.txt"
pyinstaller --onefile --noconsole gui.py  # creates single executable in "dist/" directory
mv dist/gui .
./gui
