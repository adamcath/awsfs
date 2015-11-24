#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

cd "$(dirname "$0")"
pushd . &> /dev/null

OKBLUE='\033[94m'
OKGREEN='\033[92m'
ENDC='\033[0m'
BOLD='\033[1m'

function step {
    echo -e "$BOLD$OKGREEN$(pwd)$ENDC"
    echo -e "$BOLD\$$ENDC $1"
    eval "$1"
}

echo
echo "#####################################################"
echo "# Mounting awsfs"
echo "#####################################################"
echo

mnt="$(mktemp -d /tmp/aws.XX)"
step "python "awsfs" \"$mnt\""
sleep 1  # TODO why?

function cleanup {
    cd /
    umount "$mnt"
}
trap cleanup EXIT

step "cd \"$mnt\""
step 'ls'

echo
echo "#####################################################"
echo "# Dynamo DB"
echo "#####################################################"
echo
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

echo
echo "#####################################################"
echo "# EC2"
echo "#####################################################"
echo
step 'cd ec2/us-west-2/instances'
step 'ls | head -n 10 || True'
first="$(ls | head -n 1 || True)"
step "cd $first"
step 'cat info | head -n 10'

step 'cd ../../security-groups'
step 'ls | head -n 10 || True'
first="$(ls -r | head -n 1 || True)"
step "cd $first"
step 'cat info | head -n 10'

step 'cd ../../../../'

echo
echo "#####################################################"
echo "# ELB"
echo "#####################################################"
echo
step 'cd elb/us-west-2'
step 'ls | head -n 10 || True'
first="$(ls | head -n 1 || True)"
step "cd $first"
step 'cat info | head -n 10'
step 'cat status | head -n 10'

step 'cd instances'
step 'ls -al | head -n 10 || True'

step 'cd ../security-groups'
step 'ls -al | head -n 10 || True'

echo
echo "#####################################################"
echo "# Unmounting awsfs"
echo "#####################################################"
echo

step 'cd /'

popd &> /dev/null
step "umount \"$mnt\""
trap - EXIT