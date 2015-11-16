=====
awsfs
=====

This package provides a filesystem-like interface to Amazon Web Services.

It is in early development and only provides access to a few services
(currently ec2, dynamodb, and ecs).

------------
Installation
------------

First install FUSE, a native package that allows filesystems like this one to
be implemented in userland. You can get it from https://osxfuse.github.io/ or
from homebrew::

    $ brew install Caskroom/cask/osxfuse

Only local dev installation of awsfs is currently supported::

    $ git clone https://github.com/adamcath/awsfs.git
    $ pip install --user -e awsfs

---------------
Getting started
---------------

Before you can use awsfs, you need to tell it about your AWS credentials.
The simplest way is to set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.
See the AWS docs for other methods.

Now you can mount awsfs::

    $ mkdir ~/aws  # You could put this anywhere
    $ awsfs ~/aws

Let's play around::

    $ cd ~/aws
    $ ls
    dynamo  ec2  elb
    $ cd dynamo/us-west-2
    $ ls
    some_table
    another_table

To see an automated demo, run ``demo``.