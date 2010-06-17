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
"""TODO: doc"""

raise ImportError("Pure Python backend not implemented.")

def initialize(classpath, parameters):
    return None, RemoteGraphDatabase

class RemoteGraphDatabase(object):
    def __init__(self, resource_uri, settings=None):
        pass

class IndexService(object):
    pass

INCOMING           = object()
OUTGOING           = object()
BOTH               = object()

BREADTH_FIRST      = object()
DEPTH_FIRST        = object()

ALL                = object()
ALL_BUT_START_NODE = object()
END_OF_GRAPH       = object()

def array(obj):
    return obj
def to_java(obj):
    return obj
def to_python(obj):
    return obj
def RelationshipType(type):
    return type

class NotFoundException(Exception):
    pass
class NotInTransactionException(Exception):
    pass

class Evaluator(object):
    pass
class StopAtDepth(object):
    pass
