SHELL:=/usr/bin/env bash

PROJECT_NAME = $(shell head -10 pyproject.toml|grep ^name | awk '{print $$NF}'|tr -d '"' | tr '-' '_')
PROJECT_VERSION = $(shell head -10 pyproject.toml|grep ^version | awk '{print $$NF}'|tr -d '"')
WHEEL_VERSION = $(shell echo $(PROJECT_VERSION)|sed -e 's/-dev/.dev/')
BUMP_VERSION = $(shell grep ^current_version .bumpversion.cfg | awk '{print $$NF}')
CONST_VERSION = $(shell grep ^VERSION $(PROJECT_NAME)/constants.py | awk '{print $$NF}'|tr -d '"')
TEST_MASK ?= tests/*.py

.PHONY: update
update:
	poetry update --with test --with docs
	pre-commit-update-repo.sh

.PHONY: vars
vars:
	@echo "PROJECT_NAME: $(PROJECT_NAME)"
	@echo "PROJECT_VERSION: $(PROJECT_VERSION)"
	@echo "WHEEL_VERSION: $(WHEEL_VERSION)"
	@echo "BUMP_VERSION: $(BUMP_VERSION)"
	@echo "CONST_VERSION: $(CONST_VERSION)"

.PHONY: version-sanity
version-sanity:
ifneq ($(PROJECT_VERSION), $(BUMP_VERSION))
	$(error Version mismatch PROJECT_VERSION != BUMP_VERSION)
endif
ifneq ($(PROJECT_VERSION), $(CONST_VERSION))
	$(error Version mismatch PROJECT_VERSION != CONST_VERSION)
endif
	@echo "Versions are equal $(PROJECT_VERSION), $(BUMP_VERSION), $(CONST_VERSION)"

.PHONY: black
black:
	poetry run isort $(PROJECT_NAME) $(TEST_MASK)
	poetry run black $(PROJECT_NAME) $(TEST_MASK)

.PHONY: mypy
mypy: black
	poetry run mypy $(PROJECT_NAME) $(TEST_MASK)

.PHONY: lint
lint: mypy
	poetry run flake8 $(PROJECT_NAME) $(TEST_MASK)
	poetry run doc8 -q docs

.PHONY: sunit
sunit:
	poetry run pytest -s tests

.PHONY: unit
unit:
	poetry run pytest tests

.PHONY: package
package:
	poetry check --strict
	poetry run pip check

.PHONY: publish
publish: build
	manage-tag.sh -u v$(PROJECT_VERSION)
	gh release create v$(PROJECT_VERSION) --generate-notes
	poetry publish

.PHONY: publish-test
publish-test: build
	poetry publish -r test-pypi

.PHONY: safety
safety:
	safety scan --full-report

.PHONY: nitpick
nitpick:
	poetry run nitpick -p . check

.PHONY: test
test: nitpick lint package unit

.PHONY: citest
citest: lint package unit

.PHONY: build
build: version-sanity safety clean-build test
	poetry build
	sync-wheels.sh dist/$(PROJECT_NAME)-$(WHEEL_VERSION)-py3-none-any.whl $(WHEELS)
#	manage-tag.sh -u v$(PROJECT_VERSION)

.PHONY: docs
docs:
	@cd docs && $(MAKE) $@

.PHONY: clean clean-build clean-pyc clean-test
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr docs/_build
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .cache

# vim: ft=Makefile
