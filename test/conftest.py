"""
Fixes the pytest integration bug with Pycharm.

In particular when a test fails, the the ACTUAL and EXPECTED fields
show by Pycharm is truncated if the output is too long. This bug
is applicable to Pycharm versions released before 2019-09.

Place this file in the same directory as the tests to fix the bug.

The fix is based on using a hook from pytest which might later be unsopprted.
"""


def pytest_assertrepr_compare(config, op, left, right):
    if op in ('==', '!='):
        return ['{0} {1} {2}'.format(left, op, right)]

