PYTHON ?= python3

.PHONY: validate test

validate:
	$(PYTHON) scripts/validate_skill.py

test: validate
	$(PYTHON) -m unittest discover -s tests -v
