# Variables
SOURCE = traph

# Commands
all: lint test
test: unit
publish: lint test upload clean

clean:
	rm -rf *.egg-info .pytest_cache build dist
	find . -name "*.pyc" | xargs rm

fmt:
	ruff format

lint:
	@echo Linting source code using pep8...
	ruff check traph test
	@echo

unit:
	@echo Running the unit tests...
	python -m unittest -v test
	@echo

upload:
	python setup.py sdist bdist_wheel
	twine upload dist/*
