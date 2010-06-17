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
Backend implementation for the Java platform (i.e. Jython).


 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

import warnings

from neo4j._core import BaseAdminInterface
from neo4j._compat import is_integer, is_string


def import_api():
    global INCOMING, OUTGOING, BOTH,\
        BREADTH_FIRST, DEPTH_FIRST,\
        NotFoundException,NotInTransactionException,DeadlockDetectedException,\
        ALL, ALL_BUT_START_NODE, END_OF_GRAPH,\
        Node, Relationship, NativeRelType
    from org.neo4j.graphdb.Direction import INCOMING, OUTGOING, BOTH
    from org.neo4j.graphdb.Traverser.Order import BREADTH_FIRST, DEPTH_FIRST
    from org.neo4j.graphdb import StopEvaluator, ReturnableEvaluator
    from org.neo4j.graphdb.StopEvaluator import END_OF_GRAPH
    from org.neo4j.graphdb.ReturnableEvaluator import ALL, ALL_BUT_START_NODE
    from org.neo4j.graphdb import NotFoundException, NotInTransactionException
    from org.neo4j.kernel.impl.transaction import DeadlockDetectedException
    from org.neo4j.graphdb import Node, Relationship
    from org.neo4j.graphdb import RelationshipType as NativeRelType
    return StopEvaluator, ReturnableEvaluator, NativeRelType

def make_map(m):
    return m

def initialize(classpath, parameters):
    global RelationshipType, Evaluator, StopAtDepth, IndexService,\
        array, to_java, to_python
    heap_size = parameters.pop('heap_size', None)
    if heap_size is not None:
        from java.lang import Runtime as jre; jre = jre.getRuntime()
        if is_integer(heap_size):
            heap_size *= (1024**2) # Default to megabyte
        elif heap_size[-1].isdigit():
            heap_size = int(heap_size) * (1024**2)
        else:
            heap_size = int(heap_size[:-1]) * {
                'k': 1024,
                'm': 1024**2,
                'g': 1024**3,
                't': 1024**4,
            }[heap_size[-1].lower()]
        if jre.maxMemory() < heap_size:
            warnings.warn(RuntimeWarning(
                    "Insufficient heap size!\n"
                    "Requested %s bytes, running in %s bytes." % (
                        heap_size, jre.maxMemory())))
    # Import implementation
    try:
        Stop, Returnable, Type = import_api()
    except:
        import sys
        sys.path.extend(classpath)
        Stop, Returnable, Type = import_api()
    try:
        from org.neo4j.kernel import EmbeddedGraphDatabase
    except:
        EmbeddedGraphDatabase = None
    try:
        from org.neo4j.remote import RemoteGraphDatabase
    except:
        RemoteGraphDatabase = None
    try:
        from org.neo4j.index.lucene import LuceneIndexService as IndexService
    except:
        try:
            from org.neo4j.index import NeoIndexService as IndexService
        except:
            IndexService = None
    # Define conversions
    def array(lst):
        return lst
    def to_java(obj):
        return obj
    def to_python(obj):
        return obj
    class Evaluator(Stop,Returnable):
        def __init__(self):
            self.stop = self
            self.returnable = self
    class StopAtDepth(Stop):
        def __init__(self, limit):
            limit = int(limit)
            assert limit > 0, "Illegal stop depth."
            self.__limit
        def isStopNode(self, position):
            return self.__limit <= position.depth()
    types = {}
    def RelationshipType(name):
        if name in types:
            return types[name]
        else:
            types[name] = type = RelType(name)
            return type
    class RelType(Type):
        def __init__(self, name):
            self.__name = name
        def name(self):
            return self.__name
        def __eq__(self, other):
            return self.name() == other.name()
    return EmbeddedGraphDatabase, RemoteGraphDatabase


class AdminInterface(BaseAdminInterface):
    implementation = "Jython"

    def __init__(self, neo, *more):
        try:
            self.__xa_mgr=neo.getConfig().getTxModule().getXaDataSourceManager()
        except:
            self.__xa_mgr = None
        try:
            self.__node_manager=neo.getConfig().getNeoModule().getNodeManager()
        except:
            pass
        super(AdminInterface, self).__init__(neo, *more)

    def _all_data_sources(self):
        if self.__xa_mgr is None:
            raise NotImplementedError("Cannot get datasources")
        for xa_source in self.__xa_mgr.getAllRegisteredDataSources():
            yield xa_source

    @property
    def number_of_nodes(self):
        try:
            return int(self.__node_manager.getNumberOfIdsInUse(Node))
        except:
            raise NotImplementedError("Cannot get Nodemanager")

    @property
    def number_of_relationships(self):
        try:
            return int(self.__node_manager.getNumberOfIdsInUse(Relationship))
        except:
            raise NotImplementedError("Cannot get Nodemanager")

    @property
    def number_of_relationship_types(self):
        try:
            return int(self.__node_manager.getNumberOfIdsInUse(NativeRelType))
        except:
            raise NotImplementedError("Cannot get Nodemanager")

