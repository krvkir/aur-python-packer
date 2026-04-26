.PHONY: test unit-test integration-test clean env-clean env-create env-update

test: unit-test integration-test

unit-test:
	poetry run pytest tests/test_*.py

integration-test:
	@echo "Running integration tests..."
	poetry run ./tests/integration_test.sh

env-clean:
	rm -rf .venv poetry.lock

env-create:
	poetry install

env-update:
	poetry lock
	poetry install

clean:
	rm -rf *.pkg.tar.zst
	rm -f build_state.json
	rm -rf local_repo
	find . -type d -name "__pycache__" -exec rm -rf {} +
