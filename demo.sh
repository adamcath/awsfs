#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

cd "$(dirname "$0")"

echo "#####################################################"
echo "# Mounting awsfs"
echo "#####################################################"

mnt="$(mktemp -d)"

./mount-aws.sh "$mnt"
cd "$mnt"

function cleanup {
    cd /
    umount "$mnt"
}
trap cleanup EXIT

sleep 1

function step {
    echo "> $1"
    sleep 1
    eval "$1"
    echo
    sleep 2
}

step 'ls'

echo "#####################################################"
echo "# Dynamo DB"
echo "#####################################################"
step 'cd dynamo'
step 'ls'
step 'cd us-west-2'
step 'ls | head -n 10 || True'  # TODO why?
first="$(ls | head -n 1 || True)"
step "cd $first"
step 'ls | head -n 10 || True'
first="$(ls | head -n 1 || True)"
step "cat $first"
step 'cd ../../../'

echo "#####################################################"
echo "# EC2"
echo "#####################################################"
step 'cd ec2/us-west-2/instances'
step 'ls | head -n 10 || True'
first="$(ls | head -n 1 || True)"
step "cd $first"
step 'cat info | head -n 20'
step 'cd ../../../../'

echo "#####################################################"
echo "# Unmounting awsfs"
echo "#####################################################"