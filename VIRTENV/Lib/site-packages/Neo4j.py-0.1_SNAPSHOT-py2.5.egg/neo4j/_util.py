# -*- coding: utf-8 -*-

# Copyright (c) 2008-2010 "Neo Technology,"
#     Network Engine for Objects in Lund AB [http://neotechnology.com]
# 
# This file is part of Neo4j.py.
# 
# Neo4j.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Utility functions that make working with Neo4j easier in Python.

 The available utilities are:

 * A decorator for making methods and properties handle transactions
   automatically.


 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

import neo4j

class Transactional(object):
    def __init__(self, accessor, method):
        self.accessor = accessor
        self.method = method
    def descr_get(self, obj, cls):
        method = self.method.__get__(obj, cls)
        graphdb = self.accessor.__get__(obj, cls)
        return method, graphdb
    def __call__(self, obj, *args): # for when invoked through @property
        return self.__get__(obj)(*args)

    def __get__(self, obj, cls=None):
        method, graphdb = self.descr_get(obj, cls)
        def result(*args, **kwargs):
            tx = graphdb.transaction.begin()
            try:
                try:
                    result = method(*args, **kwargs)
                except:
                    tx.failure()
                    raise
                else:
                    tx.success()
            finally:
                tx.finish()
            return result
        return result

class RetryTransactional(Transactional):
    def __get__(self, obj, cls=None):
        method, graphdb = self.descr_get(obj, cls)
        def result(*args, **kwargs):
            while True:
                tx = graphdb.transaction.begin()
                try:
                    try:
                        result = method(*args, **kwargs)
                    except neo4j.DeadlockDetectedError:
                        continue
                    except:
                        tx.failure()
                        raise
                    else:
                        tx.success()
                finally:
                    tx.finish()
                return result
        return result

def transactional(accessor, retry=False):
    def transactional(decorated):
        # Make the transactional method idempotent w/ regard to property
        if decorated is None:
            return None
        elif isinstance(decorated, property):
            return property(
                fget = transactional(decorated.fget),
                fset = transactional(decorated.fset),
                fdel = transactional(decorated.fdel),
                doc = decorated.__doc__)
        elif isinstance(decorated, Transactional):
            if decorated.accessor == accessor:
                return decorated
        if retry:
            return RetryTransactional(accessor, decorated)
        else:
            return Transactional(accessor, decorated)
    return transactional
