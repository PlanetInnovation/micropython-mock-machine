# MIT license; Copyright (c) 2020-2025, Planet Innovation
# 436 Elgar Road, Box Hill, 3128, VIC, Australia
# Phone: +61 3 9945 7510
#

default: help

.PHONY : help
help:
	@echo "mock_machine Makefile"
	@echo "Please use 'make target' where target is one of:"
	@grep -h ':\s\+##' Makefile | column -t -s# | awk -F ":" '{ print "  " $$1 "" $$2 }'

.PHONY: tests
tests:  ## Execute unit tests (inside the unix port).
tests: submodules
	@echo "-----------------------------------"
	@echo "Execute unit tests..."
	@CMD="micropython -m unittest_junit discover -s test"; \
	export MICROPYPATH=lib/micropython-lib/python-stdlib/logging:.frozen; \
	if [ -n "$${MICROPYTHON_UNIX_UNITTEST}" ]; then \
	  $${CMD}; \
	else \
	  echo "Please set MICROPYTHON_UNIX_UNITTEST=1 to run tests with your local micropython installation."; \
	  exit 1; \
	fi

.PHONY: checks
checks:  ## Run static analysis
checks: submodules
	pre-commit run --all-files

.PHONY: init
init:  ## Initialise the repository and submodules
	git init
	git submodule add https://github.com/micropython/micropython-lib.git lib/micropython-lib
	pre-commit install

.PHONY: doc-autobuild
doc-autobuild: ## Autobuild the docs so a browser can monitor changes
	docker run --rm -v $$(pwd)/doc:/doc -w /doc -p 8000:8000 minidocks/sphinx-doc sphinx-autobuild --host 0.0.0.0 . _build/

# Use submodule README.md files as a proxy for submodule init
# By adding a stem rule that will match all submodule README.md files
%/README.md:
	git submodule update --init --recursive $*

# Add more dependencies here. As more submodules are added, add a dependency on their README.md
.PHONY: submodules
submodules: ## Initalise submodules
submodules: lib/micropython-lib/README.md
