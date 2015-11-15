#!/usr/bin/env bash

usage() {
    cat <<EOF >&2
${me} path

Unmounts awsfs.

path    Where aws is currently mounted (e.g. ~/aws).
EOF
}

if [[ "$#" -ne 1 ]]; then
    usage
    exit 1
fi

umount $1

echo "awsfs has been unmounted"