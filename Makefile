#
# Copyright (c) 2020-2025 Planet Innovation Pty Ltd
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
