# AlumniFinder

The objective of this project is to develop a standalone application that automates the human user's "search and match" procedure, so that alumni relations officers can upload a list of UB alumni from their database and find them on LinkedIn.

## Build :wrench:

Clone repository and go to project root directory

Install Python Packages :package:

```
$ pip3 install -r requirements.txt
```

Linux/Mac

```
$ make build
```

Windows

* Note: Follow Pyinstaller [instructions](https://pythonhosted.org/PyInstaller/installation.html#installing-in-windows) before building

```
>>> .\winbuild.bat
```

Executable should then be located in '***dist***' directory

## Tests :pill:

Change to project root directory:

```
$ cd /path/to/AlumniFinder/
``` 

Run tests, either:

```
$ make test
```

```
$ pytest --capture=no
```