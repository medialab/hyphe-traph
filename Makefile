# Variables
SOURCE = traph

# Commands
all: lint test

test: test-unittest

lint:
	@echo Linting source code using pep8...
	pep8 $(SOURCE)
	@echo

test-unittest:
	@echo Running the unit tests...
	python -m unittest -v test
	@echo
