# AlumniFinder

The objective of this project is to develop a standalone application that leverages the LinkedIn API so that alumni relations officers can upload a list of UB alumni from their database and find them on LinkedIn.

## Build

Install Python Packages

```
$ pip3 install -r requirements.txt
```

Linux/Mac

```
$ make build
```

Windows

```
> pyinstaller --onefile --noconsole --clean ^
	--add-binary src\alumnifinder\finder\drivers\;src\alumnifinder\finder\drivers\ ^
	--add-data src\alumnifinder\gui\images\;src\alumnifinder\gui\images\ ^
	--add-data src\alumnifinder\config\;src\alumnifinder\config\ ^
	main.py
```

Executable should then be located in '*dist*' directory

## CLI

```
$ python cli.py --help 
```

## Tests

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