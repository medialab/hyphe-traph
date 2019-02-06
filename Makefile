# Variables
SOURCE = traph

# Commands
all: lint test
test: unit
publish: lint test upload clean

clean:
	rm -rf *.egg-info .pytest_cache build dist
	find . -name "*.pyc" | xargs rm

lint:
	@echo Linting source code using pep8...
	pycodestyle --ignore E501,E722,E741,W504 $(SOURCE) test
	@echo

hint:
	@echo Hinting source code using pylint...
	pylint traph | grep unused
	@echo

unit:
	@echo Running the unit tests...
	python -m unittest -v test
	@echo

upload:
	python setup.py sdist bdist_wheel
	twine upload dist/*
