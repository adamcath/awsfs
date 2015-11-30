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

function ls_and_step_into_first_dir {
    step 'ls -al | head -n 10 || True'  # TODO why?
    first="$(ls | head -n 1 || True)"
    step "cd $first"
}

function ls_and_cat_first_file {
    step 'ls | head -n 10 || True'
    first="$(ls | head -n 1 || True)"
    step "cat \"$first\""
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
ls_and_step_into_first_dir
ls_and_cat_first_file
step 'cd ../../../'

echo
echo "#####################################################"
echo "# EC2"
echo "#####################################################"
echo
step 'cd ec2/us-west-2/instances'
ls_and_step_into_first_dir
step 'cat info | head -n 10'

step 'cd ../../security-groups/by-name'
ls_and_step_into_first_dir
step 'cat info | head -n 10'

step 'cd ../../../../../'

echo
echo "#####################################################"
echo "# ELB"
echo "#####################################################"
echo
step 'cd elb/us-west-2'
ls_and_step_into_first_dir
step 'cat info | head -n 10'
step 'cat status | head -n 10'

step 'cd instances'
ls_and_step_into_first_dir
step 'cd ..'

step 'cd ../security-groups'
ls_and_step_into_first_dir
step 'cd ../../../../../'

echo
echo "#####################################################"
echo "# IAM"
echo "#####################################################"
echo

step 'cd iam'
step 'ls -l'
step 'cd users'
ls_and_step_into_first_dir
step 'ls'
step 'cat info'
step 'cd ../../'
step 'cd groups'
ls_and_step_into_first_dir
step 'ls'
step 'cat info'
step 'cd ../../'
step 'cd roles'
ls_and_step_into_first_dir
step 'ls'
step 'cat info'
step 'cd ../../'
step 'cd policies'
ls_and_step_into_first_dir
ls_and_cat_first_file
step 'cd ../../../'

echo
echo "#####################################################"
echo "# Unmounting awsfs"
echo "#####################################################"
echo

step 'cd /'

popd &> /dev/null
step "umount \"$mnt\""
trap - EXIT