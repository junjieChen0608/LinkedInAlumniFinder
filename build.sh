#!/usr/bin/env bash
# Still buggy
pyinstaller --onefile --noconsole main.py # creates single executable in "dist/" directory
mv dist/main . # move file
./main  # run app