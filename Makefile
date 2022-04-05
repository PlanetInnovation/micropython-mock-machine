#
#   Copyright (c) 2020, Planet Innovation
#   436 Elgar Road, Box Hill VIC 3128 Australia
#   Phone: +61 3 9945 7510
#
#   The copyright to the computer program(s) herein is the property of
#   Planet Innovation, Australia.
#   The program(s) may be used and/or copied only with the written permission
#   of Planet Innovation or in accordance with the terms and conditions
#   stipulated in the agreement/contract under which the program(s) have been
#   supplied.

MAKE_OPTIONS := -j$(shell nproc)

# Formatting
PYLINT_OUT := /tmp/pylint.txt
BLACK_SRC := src/firmware

default: help

.PHONY : help
help:
	@echo "mock_classes Makefile"
	@echo "Please use 'make target' where target is one of:"
	@grep -h ':\s\+##' Makefile | column -t -s# | awk -F ":" '{ print "  " $$1 "" $$2 }'

.PHONY: tests
tests:  ## Execute unit tests (inside the unix port).
	@echo "-----------------------------------"
	@echo "Execute unit tests..."
	docker run -ti --rm -v $(PWD)/lib/micropython_unittest_junit:/usr/lib/micropython -v $(PWD):/code -w /code micropython/unix micropython-dev -m test.test_mock_classes

.PHONY: checks
checks:  ## Run static analysis
checks: pre-commit run --all
