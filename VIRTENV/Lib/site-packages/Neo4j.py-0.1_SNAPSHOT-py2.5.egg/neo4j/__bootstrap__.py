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
"""XXX"""

# TODO: this is just a temporary implementation - make all modules use this
def __bootstrap__(bootstrap):
    global __bootstrap__
    def __bootstrap__(bootstrap):
        if pyneo.python.is_string(bootstrap):
            return lambda definition: definition(pyneo.newmodule(bootstrap))
        else:
            return bootstrap(pyneo)

    class pyneo(object):
        class NotInitializedError(RuntimeError): pass

        make = staticmethod(lambda factory: factory())

        pyneo = property(lambda self: pyneo)
        def newmodule(self, name):
            raise NotImplementedError("should pyneo really have modules?")

        def __call__(self, function):
            setattr(self, function.__name__, function)
            return function

        def __getattr__(self, attr):
            raise self.NotInitializedError("""Neo4j has not been initialized.
        "%s" cannot be accessed until the first NeoService is started.""" % (
                    attr,))

    pyneo = pyneo() # pyneo is a singleton

    import sys
    from neo4j import _py_compat as python_implementation
    pyneo.python = python_implementation

    #@pyneo
    #def bootstrap_neo(resource_uri, params):
    #    import neo4j._backend
    #    import neo4j._core

    return __bootstrap__(bootstrap)

@__bootstrap__
def temporary_implementation(pyneo):
    from neo4j._base import primitives, node, relationship
    pyneo.get_primitives = primitives
    pyneo.get_node = node
    pyneo.get_relationship = relationship

