#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility classes and objects for working with :mod:`concurrent.futures`.

.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import functools
import multiprocessing

import platform
_is_pypy = platform.python_implementation() == 'PyPy'

import weakref
_executors_by_base = weakref.WeakKeyDictionary()

import concurrent.futures

logger = __import__('logging').getLogger(__name__)


def ConcurrentExecutor(max_workers=None):
    """
    An abstraction layer to let code easily switch between different
    concurrency strategies. Import this instead of importing something
    from :mod:`concurrent.futures` directly.

    It also serves as a compatibility shim to make us compatible with
    gevent thread patching. For that reason, we avoid throwing any
    exceptions and instead return them, meaning that the caller should
    be prepared to get Exception objects in the results. This also
    means that for the multiprocessing case, the thrown exception
    needs to be properly pickleable. (Throwing exceptions from the
    called function is not safe in the multiprocessing case and can
    hang the pool, and has undefined results in the thread case.)

    .. note:: This strategy may change.
    """

    # Notice that we did not import the direct class because it gets swizzled at
    # runtime. For that same reason, we subclass dynamically at runtime.

    # Note: Under PyPy, there may be some benefit to using the threaded
    # worker, *IF* JIT state cannot be shared between the parent PyPy and a
    # forked child PyPy. Now, there is *SUBSTANTIAL* overhead associated with
    # forking the PyPy process (https://bitbucket.org/pypy/pypy/issue/1538/multiprocessing-slower-than-cpython);
    # the overhead is still there as-of 2.5.1 (at least), but it appears that JIT state is maintained.
    # Perhaps in general, we shouldn't be using a ConcurrentExecutor for trivial functions; if we
    # find that we are, then we should modify the API to this method to allow specifying
    # whether the function is trivial or not and thus adapt appropriately....

    # For the nti.contentrendering unit tests under PyPy, there
    # is an appreciable difference between the ThreadPoolExecutor and ProcessPoolExecutor:
    # 155s vs 275s. While unit tests are not benchmarks, for now we're defaulting PyPy to
    # the threaded executor since nti.contentrendering is one of the primary
    # consumers of this API. (this may change when threads become greenlets?)
    if _is_pypy:  # pragma: no cover
        if max_workers is None:
            max_workers = multiprocessing.cpu_count()
        base = concurrent.futures.ThreadPoolExecutor
        throw = True
    else:
        base = concurrent.futures.ProcessPoolExecutor
        throw = False

    # To assist the PyPy JIT, we cache the classes we generate
    executor = _executors_by_base.get(base)
    if executor is None:
        class _Executor(base):
            # map() channels through submit() so this captures all activity

            def submit(self, fn, *args, **kwargs):
                _fn = _nothrow(fn, _throw=throw)
                _fn = functools.update_wrapper(_fn, fn)
                return super(_Executor, self).submit(_fn, *args, **kwargs)

            def shutdown(self, *args, **kwargs):
                # The ProcessPoolExecutor spawns threads to communicate
                # with child processes, and relies on GC to clean them up.
                # While under CPython this is immediate, PyPy makes it non-deterministic.
                # This could be considered a bug in concurrent.futures, but we work around
                # it here. There are no known issues with the non-deterministic cleanup except
                # resource consumption and annoying output from test runners that track
                # "leaked" threads
                rq = getattr(self, '_result_queue', self)
                cq = getattr(self, '_call_queue', self)
                super(_Executor, self).shutdown(*args, **kwargs)
                if rq is not self:
                    try:
                        rq.close()
                    except AttributeError:  # pragma: no cover
                        pass
                    cq.close()
        executor = _executors_by_base[base] = _Executor
    return executor(max_workers)


import pickle


class _nothrow(object):
    """
    For submission to executors, a callable that doesn't throw (and
    avoids hangs.) Throwing used to result in hanging a process
    worker, but it may no longer be the case that it does in versions
    of :mod:`concurrent.futures` newer than 2.1.4. However,
    we still provide useful printing.

    For pickling, must be a top-level object.
    """

    def __init__(self, fn, _throw=False):
        self.__fn = fn
        self.__throw = _throw

    def __call__(self, *args, **kwargs):
        try:
            return self.__fn(*args, **kwargs)
        except Exception as e:
            # logging may not be reliable in this pool
            from zope.exceptions import print_exception
            import sys
            print_exception(*sys.exc_info())
            if self.__throw:
                raise
            # We'd like to return something useful, but
            # the exception itself may not be serializable
            # (and usually isn't if it has arguments and is an
            # Exception subclass---see the Python bug about this)
            try:
                pickle.loads(pickle.dumps(e))
            except Exception:
                return Exception(str(e))
            else:
                return e
