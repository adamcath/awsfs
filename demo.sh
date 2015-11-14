#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

here="$(dirname "$0")"
cd "$here"

mnt="$(mktemp -d)"
mkdir -p "$mnt"

# Start fuse in background and kill on exit
export PYTHON_PATH=src/main/python
python src/main/python/awsfs.py "$mnt" &
fuse_pid="$!"
function cleanup {
    kill "$fuse_pid"
}
trap cleanup EXIT

sleep 1

cd "$mnt"
echo "You're in!"

bash