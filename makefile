.PHONY: build clean test virtualenv

PYTHON_BIN := $(VIRTUAL_ENV)/bin

build:
	@echo "BUILD START"
	pyinstaller --onefile --noconsole --clean \
	--add-binary src/alumnifinder/finder/drivers/:src/alumnifinder/finder/drivers/ \
	--add-data src/alumnifinder/gui/images/:src/alumnifinder/gui/images/ \
	--add-data src/alumnifinder/config/:src/alumnifinder/config/ \
	main.py
	@echo "BUILD COMPLETE"

clean:
	@rm -rf *.spec
	@rm -rf dist/
	@rm -rf build/
	@rm -rf __pycache__/

test:
	pytest -n 4 --capture=no
	@rm -rf .cache/

virtualenv:
	$(PYTHON_BIN)/pip3 install -r requirements.txt
