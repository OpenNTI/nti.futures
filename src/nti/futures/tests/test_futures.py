#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that

import unittest

from nti.futures.futures import ConcurrentExecutor

from nti.futures.tests import SharedConfiguringTestLayer


def _one(unused):
    return 1


class TestFutures(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_executor(self):
        with ConcurrentExecutor() as executor:
            data = executor.map(_one, ['a', 'b'])
            assert_that(list(data), is_([1, 1]))
