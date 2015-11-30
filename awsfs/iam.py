import boto3

from format import to_json
from vfs import *


def iam_root():
    return SDir([
        ('users', CLDir(lambda: [
            (user['UserName'], SDir([
                ('info', SFile(to_json(user).encode())),
                ('groups', CLDir(lambda _user=user: [
                    (group['GroupName'], VLink('../../../groups/' + group['GroupName']))
                    for group in get_user_groups(_user)
                ])),
                ('policies', CLDir(lambda _user=user: [
                    (policy_name, VLink('../../../policies/' + policy_name))
                    for policy_name in get_user_policy_names(_user)
                ]))
            ]))
            for user in get_users()
        ])),
        ('groups', CLDir(lambda: [
            (group['GroupName'], SDir([
                ('info', SFile(to_json(group).encode())),
                ('policies', CLDir(lambda _group=group: [
                    (policy_name, VLink('../../../policies/' + policy_name))
                    for policy_name in get_group_policy_names(_group)
                ]))
            ]))
            for group in get_groups()
        ])),
        ('roles', CLDir(lambda: [
            (role['RoleName'], SDir([
                ('info', SFile(to_json(role).encode())),
                ('policies', CLDir(lambda _role=role: [
                    (policy_name, VLink('../../../policies/' + policy_name))
                    for policy_name in get_role_policy_names(_role)
                ]))
            ]))
            for role in get_roles()
        ])),
        ('policies', CLDir(lambda: [
            (policy['PolicyName'], SDir([
                ('info', SFile(to_json(policy).encode()))
            ]))
            for policy in get_policies()
        ])),
    ])


def get_client():
    return boto3.client('iam')


def get_users():
    return [
        user
        for page in get_client().get_paginator('list_users').paginate()
        for user in page['Users']
    ]


def get_user_groups(user):
    return [
        group
        for page in (get_client().
                     get_paginator('list_groups_for_user').
                     paginate(UserName=user['UserName']))
        for group in page['Groups']
    ]


def get_groups():
    return [
        group
        for page in get_client().get_paginator('list_groups').paginate()
        for group in page['Groups']
    ]


def get_roles():
    return [
        role
        for page in get_client().get_paginator('list_roles').paginate()
        for role in page['Roles']
    ]


def get_policies():
    return [
        policy
        for page in get_client().get_paginator('list_policies').paginate()
        for policy in page['Policies']
    ]


def get_user_policy_names(user):
    return [
        policy['PolicyName']
        for page in (get_client().
                     get_paginator('list_attached_user_policies').
                     paginate(UserName=user['UserName']))
        for policy in page['AttachedPolicies']
    ]


def get_group_policy_names(group):
    return [
        policy['PolicyName']
        for page in (get_client().
                     get_paginator('list_attached_group_policies').
                     paginate(GroupName=group['GroupName']))
        for policy in page['AttachedPolicies']
    ]


def get_role_policy_names(role):
    return [
        policy['PolicyName']
        for page in (get_client().
                     get_paginator('list_attached_role_policies').
                     paginate(RoleName=role['RoleName']))
        for policy in page['AttachedPolicies']
    ]
