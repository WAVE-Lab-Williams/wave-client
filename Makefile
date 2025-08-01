###############################################################################
# MAIN CONFIGURATION
###############################################################################
.PHONY: clean format

SOURCE_PATH=./python/wave_client
TESTS_DIR=./python/tests
PYTEST_LOG_LEVEL=DEBUG
PYTEST_COV_MIN=50

# Load all environment variables from .env
ifneq (,$(wildcard ./.env))
include .env
export
endif

###############################################################################
# Housekeeping
###############################################################################
clean:
	find . -type f -name ".DS_Store" -exec rm -rf {} +
	find . -type f -name "*.py[cod]" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage*" -exec rm -f {} +
	find . -type d -name "node_modules" -exec rm -rf {} +
	find . -type f -name "package-lock.json" -exec rm -f {} +

###############################################################################
# Python Development
###############################################################################

# Python formatting and linting
isort: 
	uv run isort python/

black:
	uv run black python/

flake8:
	uv run flake8 python/

pylint:
	uv run pylint python/**/*.py

format-python: isort black flake8 pylint

# Python testing
test-python-small:
	uv run pytest python/tests/small/ -rs -vv --log-level=${PYTEST_LOG_LEVEL}

test-python-all:
	uv run pytest python/tests/ -rs -vv --log-level=${PYTEST_LOG_LEVEL}

test-python-cov:
	uv run coverage run --source=${SOURCE_PATH} --omit="*/tests/*" -m pytest python/tests/ -rs -vv
	uv run coverage report --show-missing --fail-under=${PYTEST_COV_MIN}

###############################################################################
# JavaScript Development
###############################################################################

# JavaScript setup
setup-js:
	@echo "Installing JavaScript dependencies..."
	@echo "Note: If you have nvm installed, run 'nvm use' first to use the correct Node.js version"
	npm install

# JavaScript linting and formatting
lint-js:
	npm run lint

format-js:
	npm run format

format-check-js:
	npm run format:check

# JavaScript testing
test-js:
	npm test

test-js-watch:
	npm run test:watch

# JavaScript build
build-js:
	npm run build

build-js-watch:
	npm run build:watch

###############################################################################
# Combined Commands
###############################################################################

# Setup everything
setup: setup-js
	@echo "Setting up Python environment..."
	uv sync --all-extras

# Format everything
format: format-python format-js

# Test everything
test-all: test-python-all test-js

# Test small/fast tests only
test-small: test-python-small test-js

# Full CI pipeline
ci: format test-all

###############################################################################
# Local Development
###############################################################################

setup-local-dev:
	@echo "Setting up local development environment..."
	@echo "Creating Python virtual environment..."
	uv venv
	uv pip install -e .[dev,test]
	@echo "Installing JavaScript dependencies..."
	@$(MAKE) setup-js
	@echo "Checking for .env file..."
	@if [ -f .env ]; then \
		echo "✓ .env file found - using existing configuration"; \
	else \
		cp .env.example .env; \
		echo "✓ .env file created from template, please edit it to configure your environment"; \
	fi
	@echo "Local development environment ready!"