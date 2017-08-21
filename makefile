.PHONY: build clean test virtualenv

# MAKEFILE DESIGNED FOR LINUX/MAC

# DEV: Variable holding the current python virtual environment bin directory
PYTHON_BIN := $(VIRTUAL_ENV)/bin

# DEV: Builds an executable for the current operating system
build:
	@echo "BUILD START"
	pyinstaller --onefile --noconsole --clean \
	--add-binary src/alumnifinder/finder/drivers/:src/alumnifinder/finder/drivers/ \
	--add-data src/alumnifinder/gui/images/:src/alumnifinder/gui/images/ \
	--add-data src/alumnifinder/config/:src/alumnifinder/config/ \
	main.py
	@echo "BUILD COMPLETE"

# DEV: Cleans the project directory after build
clean:
	@rm -rf *.spec
	@rm -rf dist/
	@rm -rf build/
	@rm -rf __pycache__/

# DEV: Runs all tests and displays any statements to console for debugging
test:
	pytest --capture=no
	@rm -rf .cache/

# DEV: Installs required python packages to python virtual environment
virtualenv:
	$(PYTHON_BIN)/pip3 install -r requirements.txt