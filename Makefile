VIRTUAL_ENV ?= .venv

all: $(VIRTUAL_ENV)

.PHONY: help
# target: help - Display callable targets
help:
	@egrep "^# target:" [Mm]akefile

.PHONY: clean
# target: clean - Display callable targets
clean:
	rm -rf build/ dist/ docs/_build *.egg-info
	find $(CURDIR) -name "*.py[co]" -delete
	find $(CURDIR) -name "*.orig" -delete
	find $(CURDIR)/$(MODULE) -name "__pycache__" | xargs rm -rf

# ==============
#  Bump version
# ==============

.PHONY: release
VERSION?=minor
# target: release - Bump version
release:
	git checkout develop
	git pull
	git checkout master
	git merge develop
	git pull
	@poetry version $(VERSION)
	git commit -am "build(release): `poetry version -s`"
	git tag `poetry version -s`
	git checkout develop
	git merge master
	git push --tags origin develop master

.PHONY: minor
minor: release

.PHONY: patch
patch:
	make release VERSION=patch

.PHONY: major
major:
	make release VERSION=major

# =============
#  Development
# =============

$(VIRTUAL_ENV): poetry.lock .pre-commit-config.yaml
	@[ -d $(VIRTUAL_ENV) ] || python -m venv $(VIRTUAL_ENV)
	@poetry install --with tests,dev,example
	@poetry run pre-commit install
	@poetry self add poetry-bumpversion
	@touch $(VIRTUAL_ENV)

.PHONY: t test
# target: test - Runs tests
t test: $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/pytest tests.py

.PHONY: mypy
# target: mypy - Check typing
mypy: $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/mypy muffin_oauth

.PHONY: example
# target: example - Runs example
example: $(VIRTUAL_ENV)
	@$(VIRTUAL_ENV)/bin/uvicorn example:app --reload --port 5000
