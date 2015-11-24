import boto3

from format import to_json
from vfs import *


regions = [
    "ap-northeast-1", "ap-southeast-1", "ap-southeast-2",
    "eu-central-1", "eu-west-1", "sa-east-1", "us-east-1",
    "us-west-1", "us-west-2"
]


def get_client(region):
    return boto3.client('elb', region_name=region)


def elb_root():

    def load():
        return [(region_name, elb_region(region_name))
                for region_name in regions]

    return CachedLazyReadOnlyDir(load, -1)


def elb_region(region):

    def load():
        result = []
        for page in (get_client(region).
                     get_paginator('describe_load_balancers').
                     paginate()):
            for elb in page['LoadBalancerDescriptions']:
                elb_id = elb['LoadBalancerName']
                result.append(
                    (elb_id,
                     elb_dir(region, elb_id, elb)))
        return result

    return CachedLazyReadOnlyDir(load, 60)


def elb_dir(region, elb_id, elb_obj):

    def load():
        return [
            ("info", StaticFile(to_json(elb_obj).encode())),
            ("status", elb_instance_status_file(region, elb_id)),
            ("instances", elb_instances_dir(region, elb_obj)),
            ("security-groups", elb_security_groups_dir(region, elb_obj))
        ]

    return CachedLazyReadOnlyDir(load, -1)


def elb_instance_status_file(region, elb_id):

    def load():
        statuses = (get_client(region).
                    describe_instance_health(LoadBalancerName=elb_id)
                    ['InstanceStates'])
        return to_json(statuses).encode()

    return LazyReadOnlyFile(load)


def elb_instances_dir(region, elb_obj):

    def load():
        result = []
        for instance in elb_obj['Instances']:
            instance_id = instance['InstanceId']
            path = '../../../../ec2/%s/instances/%s' % (region, instance_id)
            result.append((instance['InstanceId'], VLink(path)))
        return result

    return CachedLazyReadOnlyDir(load, -1)


def elb_security_groups_dir(region, elb_obj):

    def load():
        result = []
        for security_group_id in elb_obj['SecurityGroups']:
            path = ('../../../../ec2/%s/security-groups/%s' %
                    (region, security_group_id))
            result.append((security_group_id, VLink(path)))
        return result

    return CachedLazyReadOnlyDir(load, -1)
