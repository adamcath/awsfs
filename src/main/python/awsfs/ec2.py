import boto3

from format import to_json
from vfs import *


regions = [
    "ap-northeast-1", "ap-southeast-1", "ap-southeast-2",
    "eu-central-1", "eu-west-1", "sa-east-1", "us-east-1",
    "us-west-1", "us-west-2"
]


def get_client(region):
    return boto3.client('ec2', region_name=region)


def ec2_root():

    def load():
        return [(region_name, ec2_region(region_name))
                for region_name in regions]

    return CachedLazyReadOnlyDir(load, -1)


def ec2_region(region):

    def load():
        return [("instances", ec2_instances_dir(region))]

    return CachedLazyReadOnlyDir(load, -1)


def ec2_instances_dir(region):

    def load():
        result = []
        for page in (get_client(region).
                     get_paginator('describe_instances').
                     paginate()):
            for reservation in page['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    result.append(
                        (instance_id,
                         ec2_instance_dir(region, instance_id, instance)))
        return result

    return CachedLazyReadOnlyDir(load, 60)


def ec2_instance_dir(region, instance_id, instance_obj):

    def load():
        return [
            ("info", StaticFile(to_json(instance_obj).encode())),
            ("status", ec2_instance_status_file(region, instance_id))
        ]

    return CachedLazyReadOnlyDir(load, -1)


def ec2_instance_status_file(region, instance_id):

    def load():
        statuses = (get_client(region).
                    describe_instance_status(InstanceIds=[instance_id])
                    ['InstanceStatuses'])
        if len(statuses) == 0:
            return 'null'
        return to_json(statuses[0]).encode()

    return LazyReadOnlyFile(load)
