PYTHON = python3

VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_DONE = $(VENV)/.done
VENV_PIP_INSTALL = '.[dev, test]'
VENV_SYSTEM_SITE_PACKAGES = $(VENV)/.venv-system-site-packages
VENV_USE_SYSTEM_SITE_PACKAGES = $(wildcard $(VENV_SYSTEM_SITE_PACKAGES))

.PHONY: venv-system-site-packages
venv-system-site-packages: override VENV_USE_SYSTEM_SITE_PACKAGES := 1
venv-system-site-packages: $(VENV_DONE)

.PHONY: venv
venv: $(VENV_DONE)

.PHONY: pipx
pipx:
	pipx install --editable .

.PHONY: pipx-site-packages
pipx-site-packages:
	pipx install --system-site-packages --editable .

.PHONY: check
check: lint test readme

.PHONY: lint
lint: lint-flake8 lint-mypy lint-isort

LINT_SOURCES = src/ tests/

.PHONY: lint-flake8
lint-flake8: $(VENV_DONE)
	$(VENV_PYTHON) -m flake8 $(LINT_SOURCES)

.PHONY: lint-mypy
lint-mypy: $(VENV_DONE)
	$(VENV_PYTHON) -m mypy --show-column-numbers $(LINT_SOURCES)

.PHONY: lint-isort
lint-isort: $(VENV_DONE)
	$(VENV_PYTHON) -m isort --check $(LINT_SOURCES)

.PHONY: test
test: $(VENV_DONE)
	$(VENV_PYTHON) -m pytest $(PYTEST_FLAGS) tests/

.PHONY: readme
readme: README.md $(wildcard src/liscopridge/app/*.md)

%.md: INTERACTIVE=$(shell [ -t 0 ] && echo --interactive)
%.md: $(VENV_DONE) _phony
	PATH="$(CURDIR)/$(VENV)/bin:$$PATH" \
	$(VENV_PYTHON) -m cram --indent=4 $(INTERACTIVE) $@

.PHONY: dist
dist: $(VENV_DONE)
	rm -rf dist/
	$(VENV_PYTHON) -m build --outdir dist

.PHONY: twine-upload
twine-upload: dist
	$(VENV_PYTHON) -m twine upload $(wildcard dist/*)

.PHONY: ipython
ipython: $(VENV_DONE)
	$(VENV_PYTHON) -m IPython

.PHONY: clean
clean:
	git clean -ffdX

define VENV_CREATE
	$(PYTHON) -m venv $(VENV)
	$(VENV_PYTHON) -m pip install wheel
endef

define VENV_CREATE_SYSTEM_SITE_PACKAGES
	$(PYTHON) -m venv --system-site-packages --without-pip $(VENV)
	$(VENV_PYTHON) -m pip --version || $(PYTHON) -m venv --system-site-packages $(VENV)
	touch $(VENV_SYSTEM_SITE_PACKAGES)
endef

# workaround for https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1003252 and/or https://github.com/pypa/pip/issues/6264
ifdef VENV_USE_SYSTEM_SITE_PACKAGES
$(VENV_DONE): export SETUPTOOLS_USE_DISTUTILS := stdlib
endif

$(VENV_DONE): $(MAKEFILE_LIST) setup.py setup.cfg pyproject.toml
	$(if $(VENV_USE_SYSTEM_SITE_PACKAGES),$(VENV_CREATE_SYSTEM_SITE_PACKAGES),$(VENV_CREATE))
	$(VENV_PYTHON) -m pip install -e $(VENV_PIP_INSTALL)
	touch $@

.PHONY: _phony
