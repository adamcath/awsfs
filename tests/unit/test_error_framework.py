import unittest
from errno import *
from logging import INFO, WARNING, ERROR

from botocore.exceptions import NoCredentialsError, \
    PartialCredentialsError, ClientError
from fuse import FuseOSError

import awsfs


class TestOperationWrapper(unittest.TestCase):

    def test_when_an_op_returns_then_propagate_it(self):
        self.assertEqual(MyAwsOps().__call__('good_op', 42), 42)

    def test_when_an_op_throws_boto_error_then_convert_it(self):
        with self.assertRaises(FuseOSError):
            MyAwsOps().__call__('bad_op', IOError('cant talk to aws'))

    def test_when_an_op_throws_fuseoserror_then_let_it_pass(self):
        with self.assertRaises(FuseOSError):
            MyAwsOps().__call__('bad_op', FuseOSError(ENOENT))

    def test_when_an_op_throws_programming_error_then_crash(self):
        ops = MyAwsOps()
        ops.__call__('bad_op', ArithmeticError('div by zero!'))
        assert ops.crashed

    def test_when_an_op_throws_and_parsing_fails_then_crash(self):
        ops = AwsOpsWithBadExConverter()
        ops.__call__('bad_op', IOError('cant talk to aws!'))
        assert ops.crashed

    def test_to_fuse_ex(self):
        def case(ex, expected_errno, expected_log_level):
            (fuse_ex, log_level) = awsfs.AwsOps().to_fuse_ex(ex)
            self.assertEqual(fuse_ex.errno, expected_errno)
            self.assertEqual(log_level, expected_log_level)

        # ClientError with code
        case(ClientError({'Error': {'Code': 'ResourceNotFoundException'}}, 'scan'), ENOENT, INFO)
        case(ClientError({'Error': {'Code': 'AuthFailure'}}, 'scan'), EPERM, WARNING)
        case(ClientError({'Error': {'Code': 'UnauthorizedOperation'}}, 'scan'), EPERM, WARNING)
        case(ClientError({'Error': {'Code': 'Blocked'}}, 'scan'), EPERM, WARNING)

        # Code missing or not recognized, but useful HTTPStatusCode
        case(ClientError({'Error': {'HTTPStatusCode': 401}}, 'scan'), EPERM, WARNING)
        case(ClientError({'Error': {'HTTPStatusCode': 402}}, 'scan'), EPERM, WARNING)
        case(ClientError({'Error': {'HTTPStatusCode': 403}}, 'scan'), EPERM, WARNING)
        case(ClientError({'Error': {'HTTPStatusCode': 404}}, 'scan'), ENOENT, INFO)
        case(ClientError({'Error': {'HTTPStatusCode': 409}}, 'scan'), ESTALE, WARNING)
        case(ClientError({'Error': {'HTTPStatusCode': 410}}, 'scan'), ENOENT, INFO)
        case(ClientError({'Error': {'HTTPStatusCode': 500}}, 'scan'), EIO, WARNING)
        case(ClientError({'Error': {'HTTPStatusCode': 501}}, 'scan'), EIO, WARNING)

        # Unrecognized HTTPStatusCode
        case(ClientError({'Error': {'HTTPStatusCode': 300}}, 'scan'), EIO, ERROR)

        # No code OR HTTPStatusCode
        case(ClientError({'Error': {}}, 'scan'), EIO, ERROR)

        # Misc boto errors
        case(IOError('cant talk to aws!'), EIO, WARNING)
        case(NoCredentialsError(), ENOLINK, WARNING)
        case(PartialCredentialsError(provider='test', cred_var='test'), ENOLINK, WARNING)


class MyAwsOps(awsfs.AwsOps):

    def __init__(self):
        super(MyAwsOps, self).__init__()
        self.crashed = False

    def good_op(self, result):
        return result

    def bad_op(self, exception):
        raise exception

    def crash(self):
        self.crashed = True


class AwsOpsWithBadExConverter(MyAwsOps):

    def to_fuse_ex(self, e):
        raise Exception('conversion failed')
