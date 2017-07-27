.PHONY: clean build virtualenv

PYTHON_BIN := $(VIRTUAL_ENV)/bin

build:
	@echo "BUILD START"
	pyinstaller --onefile --noconsole main.py
	@echo "BUILD COMPLETE"

clean:
	@rm -rf *.spec
	@rm -rf dist/
	@rm -rf build/
	@rm -rf __pycache__/

virtualenv:
	$(PYTHON_BIN)/pip3 install -r requirements.txt	
