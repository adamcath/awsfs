=====
awsfs
=====

|Build Status|

This package provides a filesystem-like interface to Amazon Web Services.

It is in early development and only provides access to a few services
(currently ec2, dynamodb, and elb).

.. |Build Status| image:: https://travis-ci.org/adamcath/awsfs.svg?branch=master
    :target: https://travis-ci.org/adamcath/awsfs
    :alt: Build Status

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

To see an automated demo, run ``./demo.sh``. The demo uses YOUR AWS account,
so it's best if you have some stuff in there.

-------------
Running tests
-------------

Once you've installed awsfs (see above)::

    $ pip install -r requirements.txt
    $ ./unit_tests.sh
    test_when_an_op_returns_then_propagate_it (test_error_framework.TestOperationWrapper) ... ok
    ...
    Ran 4 tests in 0.001s

    OK

--------------
TODO for beta
--------------

The project is in a very early state. It's more convenient to track all the
un-done stuff here than in a lot of separate issues.

- Tests
- Which services should we support?
- Paging: a Dynamo table could be a very big directory. Sadly Fusepy appears
  to hide the streaming directory APIs.
- Modeling: what are the principals behind whether something is a file or dir?
  Currently its a judgment call.
- Modeling: let's represent links between things in a consistent way.
- Multi-threading: I *think* it's thread-safe now, but I don't understand FUSE's
  threading model well enough to be confident.
- Permissions: can we map from AWS?
- Caching: Currently most things are just on a 60 second cache, period.
  Can we do better (e.g. if you modify something through awsfs, you should
  probably see those writes immediately).
- Logging: do more. Is syslog really appropriate?
- Writes: currently it's read only. There are some cases where writing directly
  would be natural (e.g. dynamo, s3), and other cases where it might make
  more sense to expose "programs" (cd ec2/<instance-id>; terminate).
- Queries: make it easy to search dynamo/s3 not by primary key? You can use
  grep but it's very inefficient and not always natural.
  e.g. cd dynamo-table; query firstname=foo
  Is this in scope?
- getattr returns some fake values (size, timestamps). Does it matter? Can we
  improve without loading the whole things?
- Implement statfs?