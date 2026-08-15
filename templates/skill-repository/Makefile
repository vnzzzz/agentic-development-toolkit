PYTHON ?= python3

.PHONY: validate test-distribution test

validate:
	$(PYTHON) scripts/validate_skill.py

test-distribution:
	$(PYTHON) scripts/validate_distribution.py

test: validate test-distribution
	$(PYTHON) -m unittest discover -s tests -v
