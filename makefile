.PHONY: clean docker-image build test virtualenv

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

test:
	python3 -m pytest --capture=no tests/
	@rm -rf .cache/

docker-image:
	docker build -t alumni-finder-machine .
