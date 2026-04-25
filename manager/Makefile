VENV=venv
PYTHON=$(VENV)/bin/python
PYTEST=$(VENV)/bin/pytest

.PHONY: test unit-test integration-test clean venv

test: unit-test integration-test

unit-test: venv
	PYTHONPATH=src $(PYTEST) tests/test_*.py

integration-test: venv
	@echo "Running integration tests..."
	./tests/integration_test.sh

venv: $(VENV)/bin/activate

$(VENV)/bin/activate: pyproject.toml
	python -m venv $(VENV)
	$(VENV)/bin/pip install .
	$(VENV)/bin/pip install pytest networkx requests jinja2 click
	touch $(VENV)/bin/activate

clean:
	rm -rf $(VENV)
	rm -rf *.pkg.tar.zst
	rm -f build_state.json
	rm -rf local_repo
	find . -type d -name "__pycache__" -exec rm -rf {} +
