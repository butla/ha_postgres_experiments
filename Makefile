.PHONY: build clean

SHELL:=/bin/bash

build_venv:
	virtualenv -p python3.8 venv
	$(shell source venv/bin/activate; poetry install)

