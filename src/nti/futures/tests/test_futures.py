#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import assert_that

import unittest

from nti.futures.futures import _nothrow
from nti.futures.futures import ConcurrentExecutor

from nti.futures.tests import SharedConfiguringTestLayer


def _one(unused_arg):
    return 1


class TestFutures(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_executor(self):
        with ConcurrentExecutor() as executor:
            data = executor.map(_one, ['a', 'b'])
            assert_that(list(data), is_([1, 1]))

    def test_nothrow(self):
        def _raise():
            raise Exception()
        fn = _nothrow(_raise, False)
        assert_that(fn(), is_(Exception))

        fn = _nothrow(_raise, True)
        with self.assertRaises(Exception):
            fn()

        class V(ValueError):
            def __reduce_ex__(self, protocol=0):
                raise TypeError()
            __reduce__ = __reduce_ex__
        
        def _v_ex():
            raise V("value")
        fn = _nothrow(_v_ex, False)
        assert_that(fn(), is_(Exception))
