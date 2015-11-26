#!/usr/bin/env bash

set -o errexit

echo '#################################################'
echo '# Running unit tests'
echo '#################################################'

coverage run --branch -m unittest discover tests/unit/ -v

echo
echo '#################################################'
echo '# Coverage report'
echo '#################################################'

coverage_omissions="$HOME/Library/**,/Library/**"

coverage annotate --omit="$coverage_omissions" -d build/coverage

if ! coverage report --omit="$coverage_omissions" --fail-under=40; then
    echo 'FAILED: Coverage too low' 2>&1
    exit 2
fi
echo 'Coverage OK. Annotated src in build/coverage'