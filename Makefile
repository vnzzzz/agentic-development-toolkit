PYTHON ?= python3

.PHONY: validate link-skills workspace-test test audit doctor clean bootstrap

validate:
	$(PYTHON) scripts/skill_workspace.py validate

link-skills:
	$(PYTHON) scripts/skill_workspace.py link

workspace-test:
	$(PYTHON) -m unittest discover -s tests -v

test: workspace-test audit

audit:
	$(PYTHON) scripts/security_audit.py

doctor:
	$(PYTHON) scripts/skill_workspace.py doctor

bootstrap:
	bash scripts/bootstrap-local.sh

clean:
	rm -rf build .venv .pytest_cache .ruff_cache
	find scripts tests templates -type d -name __pycache__ -prune -exec rm -rf {} +
