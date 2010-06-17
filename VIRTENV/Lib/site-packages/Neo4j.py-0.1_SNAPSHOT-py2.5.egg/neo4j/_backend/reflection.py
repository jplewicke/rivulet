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
Backend implementation for the CPython platform using JPype reflection.


 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

import jpype

from neo4j._core import BaseAdminInterface
from neo4j._compat import is_integer, is_string


def initialize(classpath, parameters):
    global INCOMING, OUTGOING, BOTH,\
        BREADTH_FIRST, DEPTH_FIRST,\
        NotFoundException,NotInTransactionException,DeadlockDetectedException,\
        RelationshipType, Evaluator, IndexService,\
        ALL, ALL_BUT_START_NODE, END_OF_GRAPH, StopAtDepth,\
        array, to_java, to_python, tx_join, make_map,\
        Node, Relationship, NativeRelType
    jvm = parameters.pop('jvm', None)
    if jvm is None:
        jvm = jpype.getDefaultJVMPath()
    args = []
    if 'ext_dirs' in parameters:
        args.append('-Djava.ext.dirs=' + ':'.join(parameters['ext_dirs']))
    args.append('-Djava.class.path=' + ':'.join(classpath))
    heap_size = parameters.pop('heap_size', None)
    if heap_size is not None:
        if is_integer(heap_size) or heap_size[-1].isdigit():
            heap_size = '%sM' % heap_size # default to megabyte
        args.append('-Xmx' + heap_size)
    jpype.startJVM(jvm, *args)
    core = jpype.JPackage('org').neo4j.graphdb
    kernel_impl = jpype.JPackage('org').neo4j.kernel.impl
    INCOMING = core.Direction.INCOMING
    OUTGOING = core.Direction.OUTGOING
    BOTH = core.Direction.BOTH
    Order = getattr(core, 'Traverser$Order')
    Stop = core.StopEvaluator
    Returnable = core.ReturnableEvaluator
    BREADTH_FIRST = Order.BREADTH_FIRST
    DEPTH_FIRST = Order.DEPTH_FIRST
    ALL = Returnable.ALL
    ALL_BUT_START_NODE = Returnable.ALL_BUT_START_NODE
    END_OF_GRAPH = Stop.END_OF_GRAPH
    NotFoundException = jpype.JException(core.NotFoundException)
    NotInTransactionException = jpype.JException(core.NotInTransactionException)
    DeadlockDetectedException = jpype.JException(
        kernel_impl.transaction.DeadlockDetectedException)
    Node = core.Node
    Relationship = core.Relationship
    NativeRelType = core.RelationshipType
    try:
        EmbeddedGraphDb = jpype.JClass("org.neo4j.kernel.EmbeddedGraphDatabase")
    except:
        EmbeddedGraphDb = None
    try:
        RemoteGraphDb = jpype.JClass("org.neo4j.remote.RemoteGraphDatabase")
    except:
        RemoteGraphDb = None
    try:
        IndexService = jpype.JClass("org.neo4j.index.lucene.LuceneIndexService")
    except:
        try:
            IndexService = jpype.JClass("org.neo4j.index.NeoIndexService")
        except:
            IndexService = None

    HashMap = jpype.java.util.HashMap
    def make_map(d):
        result = HashMap()
        for key, value in d.items():
            result.put(key, value)
        return result

    def tx_join():
        if not jpype.isThreadAttachedToJVM():
            jpype.attachThreadToJVM()

    def array(lst):
        return lst

    def to_java(obj):
        return obj

    def to_python(obj):
        return obj

    rel_types = {}
    def RelationshipType(name):
        if name in rel_types:
            return rel_types[name]
        else:
            rel_types[name] = type = jpype.JProxy(core.RelationshipType,dict={
                    'name': lambda:name
                    })
            return type

    def StopAtDepth(limit):
        limit = int(limit)
        assert limit > 0, "Illegal stop depth."
        if limit == 1:
            return core.StopEvaluator.DEPTH_ONE
        else:
            return jpype.JProxy(Stop, dict={
                    'isStopNode': lambda pos: limit <= pos.depth()
                    })
    class Evaluator(object):
        def __init__(self):
            self.stop = jpype.JProxy(Stop, inst=self)
            self.returnable = jpype.JProxy(Returnable, inst=self)
    return EmbeddedGraphDb, RemoteGraphDb


class AdminInterface(BaseAdminInterface):
    implementation = "JPype"

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
            return int(
                self.__node_manager.getNumberOfIdsInUse(NativeRelType))
        except:
            raise NotImplementedError("Cannot get Nodemanager")

