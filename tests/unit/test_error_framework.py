import unittest
import errno
from fuse import FuseOSError

import awsfs


class TestOperationWrapper(unittest.TestCase):

    def test_when_an_op_returns_then_propagate_it(self):
        self.assertEqual(MyAwsOps().__call__('good_op', 42), 42)

    def test_when_an_op_throws_fuseoserror_then_let_it_pass(self):
        with self.assertRaises(FuseOSError):
            MyAwsOps().__call__('bad_op', FuseOSError(errno.ENOENT))

    def test_when_an_op_throws_programming_error_then_crash(self):
        ops = MyAwsOps()
        ops.__call__('bad_op', ArithmeticError('div by zero!'))
        assert ops.crashed

    def test_when_an_op_throws_ioerror_then_convert_it(self):
        with self.assertRaises(FuseOSError):
            MyAwsOps().__call__('bad_op', IOError('cant talk to aws!'))


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
