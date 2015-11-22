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

if ! coverage report --omit="$HOME/Library/**,/Library/**" --fail-under=40; then
    echo 'FAILED: Coverage too low' 2>&1
fi