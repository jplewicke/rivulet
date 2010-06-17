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
This module defines the basic behaviour for all Neo4j.py objects.


 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

class Neo4jObject(object):
    """This class is the base class of all Neo4j.py objects."""
    def __init__(self, neo=None, node=None, relationship=None):
        self.__neo4j__neo = neo
        self.__neo4j__node = node
        self.__neo4j__relationship = relationship
def primitives(obj):
    """Circumvent name mangling to get internals."""
    return obj._Neo4jObject__neo4j__neo,\
        obj._Neo4jObject__neo4j__node,\
        obj._Neo4jObject__neo4j__relationship
def node(obj):
    """Circumvent name mangling to get node."""
    return obj._Neo4jObject__neo4j__node
def relationship(obj):
    """Circumvent name mangling to get relationship."""
    return obj._Neo4jObject__neo4j__relationship
