#!/bin/bash

export PATH="$PYTHON_HOME/bin:$PATH"

pip install poetry
poetry install
poetry build

mkdir wheels

for wheel in dist/*.whl; do
    auditwheel repair "$wheel" --plat $PLATFORM -w wheels/
done