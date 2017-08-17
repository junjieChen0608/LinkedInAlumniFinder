pyinstaller --onefile --noconsole --clean ^
	--add-binary src\alumnifinder\finder\drivers\;src\alumnifinder\finder\drivers\ ^
	--add-data src\alumnifinder\gui\images\;src\alumnifinder\gui\images\ ^
	--add-data src\alumnifinder\config\;src\alumnifinder\config\ ^
	main.py
