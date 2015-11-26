import boto3

from vfs import *

import logging


log = logging.getLogger('s3')


def s3_root():
    return CLDir(lambda: [
        (bucket, CLDir(lambda _bucket=bucket:
                       get_dirents(get_bucket_region(_bucket), _bucket)))
        for bucket in get_bucket_names()
    ])


def get_client(region):
    return boto3.client('s3', region_name=region)


def get_bucket_names():
    return [
        bucket['Name']
        for bucket in get_client('us-west-2').list_buckets()['Buckets']
    ]


def get_bucket_region(bucket):
    return (get_client('us-west-2').
            get_bucket_location(Bucket=bucket)['LocationConstraint'])


def get_dirents(region, bucket, prefix=''):
    result = []
    for page in (get_client(region).
                 get_paginator('list_objects').
                 paginate(Bucket=bucket, Delimiter='/', Prefix=prefix)):

        # Files
        for item in page.get('Contents') or []:
            key = item['Key']  # Fully qualified
            if key.endswith('/'):
                # Sometimes the subdir itself is returned. Drop it
                continue
            log.info(key + ": " + key.split('/')[-1])
            result.append((key.split('/')[-1],
                           LFile(lambda _key=key:
                                 get_item_file(region, bucket, _key),
                                 item['Size'])))

        # Subdirs
        for subdir_obj in page.get('CommonPrefixes') or []:
            subdir = subdir_obj['Prefix']  # Fully qualified with trailing /
            result.append((subdir.rstrip('/').split('/')[-1],
                           CLDir(lambda _subdir=subdir:
                                 get_dirents(region, bucket, _subdir))))
    return result


def get_item_file(region, bucket, key):
    return (boto3.resource('s3', region_name=region).
            Object(bucket, key).get()['Body'].read())
