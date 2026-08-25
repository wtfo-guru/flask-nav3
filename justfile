#!/usr/bin/env just --justfile

dir_path := "src"
src_path := shell('test -d $1 && echo "src" || echo "."', dir_path)

# use these when not testing < python 3.11
# PROJECT_NAME := `python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])"`
# PROJECT_VERSION := `python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])"`
# use these when testing < python 3.11
PROJECT_NAME := shell("grep ^name pyproject.toml | head -1 | awk '{print $NF}' | tr -d '\"'")
PROJECT_VERSION := shell("grep ^version pyproject.toml | head -1 | awk '{print $NF}' | tr -d '\"'")
PACKAGE_BASE := shell('echo $1 | tr "-" "_"', PROJECT_NAME)
PACKAGE_DIR := shell('echo $1/$2', src_path, PACKAGE_BASE)
BUMP_VERSION := `grep ^current_version .bumpversion.cfg | awk '{print $NF}'`
CONST_VERSION := PROJECT_VERSION
# TEST_FILES := './tests/**/*.py'
TEST_FILES := "./tests/*.py"

# hello is recipe's name
vars:
  @echo "PROJECT_NAME: {{PROJECT_NAME}}"
  @echo "PROJECT_VERSION: {{PROJECT_VERSION}}"
  @echo "PACKAGE_BASE: {{PACKAGE_BASE}}"
  @echo "PACKAGE_DIR: {{PACKAGE_DIR}}"
  @echo "BUMP_VERSION: {{BUMP_VERSION}}"
  @echo "CONST_VERSION: {{CONST_VERSION}}"

version-sanity:
  #!/usr/bin/env bash
  set -euo pipefail
  if [[ "{{PROJECT_VERSION}}" != "{{BUMP_VERSION}}" ]]; then
    echo "Version mismatch PROJECT_VERSION != BUMP_VERSION"
    exit 1
  elif [[ "{{PROJECT_VERSION}}" != "{{CONST_VERSION}}" ]]; then
    echo "Version mismatch PROJECT_VERSION != CONST_VERSION"
    exit 1
  else
    echo "Versions are equal {{PROJECT_VERSION}}, {{BUMP_VERSION}}, {{CONST_VERSION}}"
  fi

changelog-check:
  #!/usr/bin/env bash
  set -euo pipefail
  error() { echo "$@" >&2 ; exit 1; }
  if echo "{{PROJECT_VERSION}}" | grep -q "dev"; then
    error "Cannot pull request when dev version"
  elif ! grep -qP "^## \[{{PROJECT_VERSION}}\] - \d\d\d\d-\d\d-\d\d\$" CHANGELOG.md; then
    error "No changelog entry for {{PROJECT_VERSION}}"
  elif grep -q "Unreleased" CHANGELOG.md; then
    error "Unreleased section in CHANGELOG.md"
  else
    echo "Changelog entry found for {{PROJECT_VERSION}}"
  fi

ruff:
	@poetry run ruff check --fix {{PACKAGE_DIR}} {{TEST_FILES}}

mypy: ruff
	@poetry run mypy {{PACKAGE_DIR}}
# TODO: Add {{TEST_FILES}} when time permits

lint: mypy
	@poetry run flake8 {{PACKAGE_DIR}} {{TEST_FILES}}

package:
	@poetry run pip check

unit:
	@poetry run pytest {{TEST_FILES}}

safety:
  #!/usr/bin/env bash
  set -euo pipefail
  if head -1 /etc/systemd/resolved.conf.d/local.conf | grep -q roaming ; then
    safety scan --full-report
  else
    safety --proxy-host squid.metaorg.com --proxy-port 3128 --proxy-protocol http scan --full-report
  fi

nitpick:
	@nitpick -p . check

test: nitpick lint package unit

candidate: test

citest: lint package unit

poetry-update:
	@poetry update --with dev --with docs

update: poetry-update safety
	@pre-commit-update-repo.sh

build: version-sanity changelog-check
	@poetry build

publish: clean build
  #!/usr/bin/env bash
  set -euo pipefail
  export UV_PUBLISH_USERNAME="${USER}"
  export UV_PUBLISH_PASSWORD="$(wtfpass --db "$USER" show --plain pypi/metaorg)"
  uv publish "--index" metaorg

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	@rm -fr build/
	@rm -fr docs/_build
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	@rm -fr .tox/
	@rm -f .coverage
	@rm -fr htmlcov/
	@rm -fr .pytest_cache
	@rm -fr .mypy_cache
	@rm -fr .ruff_cache
	@rm -fr .cache
