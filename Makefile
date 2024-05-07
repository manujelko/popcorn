# ==================================================================================== #
# HELPERS
# ==================================================================================== #

## help: print this help message
.PHONY: help
help:
	@echo 'Usage:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' | sed -e 's/^/ /'


.PHONY: confirm
confirm:
	@echo -n 'Are you sure? [y/N] ' && read ans && [ $${ans:-N} = y ]


# ==================================================================================== #
# DEVELOPMENT
# ==================================================================================== #

## secret_key: generate secret key
.PHONY: secret_key
.PHONY:secret_key
secret_key:
	@echo "Generating secret key"
	openssl rand -hex 32


## run/api: run the api
.PHONY: run/api
run/api:
	uvicorn app.main:app --reload


# ==================================================================================== #
# QUALITY CONTROL
# ==================================================================================== #

## audit: format, lint, type check and test all code.
.PHONY: audit
audit:
	@echo 'Formatting code...'
	python -m ruff format app tests
	python -m ruff check --select I --fix app tests
	@echo 'Linting code...'
	python -m ruff check app tests
	@echo 'Type checking code...'
	python -m mypy app tests
	@echo 'Running tests...'
	python -m pytest -v
