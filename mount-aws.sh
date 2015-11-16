#!/usr/bin/env bash
#
# Mounts a virtual device in the filesystem in which you can access
# various AWS services, treating them like directories and files.
#
# Run with no args for usage.

set -o errexit
set -o pipefail
set -o nounset

me="$(basename "$0")"
here="$(dirname "$0")"

usage() {
    cat <<EOF >&2
${me} path

Mounts a virtual device in the filesystem in which you can access
various AWS services, treating them like directories and files.

Your AWS credentials should be in your environment. The simplest way
is to set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. See the AWS docs
for other methods.

path    Where awsfs should be mounted (e.g. ~/aws).
        Must be a directory that exists and you can write.
EOF
}

if [[ "$#" -ne 1 ]]; then
    usage
    exit 1
fi

mnt="$1"

python "$here/awsfs" "$mnt"

echo "awsfs is now available at $mnt"
echo "Logs are in the system log"