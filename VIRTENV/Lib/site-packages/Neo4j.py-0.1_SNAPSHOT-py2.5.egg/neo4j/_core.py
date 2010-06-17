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
This module dispatches the implementation.


 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

import threading

from neo4j._base import Neo4jObject
from neo4j._compat import is_string, is_integer


BASIC_NEO4J_OPTIONS = [
    # Cache
    'min_node_cache_size',
    'max_node_cache_size',
    'min_relationship_cache_size',
    'max_relationship_cache_size',
    'adaptive_cache_heap_ratio',
    'adaptive_cache_manager_decrease_ratio',
    'use_adaptive_cache',
    'adaptive_cache_worker_sleep_time',
    'adaptive_cache_manager_increase_ratio',
    # Memory mapping
    'use_memory_mapped_buffers',
]
NEO4J_OPTIONS = {
    # Memory mapping
    'mmap_nodestore': 'neostore.nodestore.db.mapped_memory',
    'mmap_relationshipstore': 'neostore.relationshipstore.db.mapped_memory',
    'mmap_propertystore': 'neostore.propertystore.db.mapped_memory',
    'mmap_property_keys': 'neostore.propertystore.db.index.keys.mapped_memory',
    'mmap_property_index': 'neostore.propertystore.db.index.mapped_memory',
    'mmap_property_strings': 'neostore.propertystore.db.strings.mapped_memory',
    'mmap_property_arrays': 'neostore.propertystore.db.arrays.mapped_memory',
}
for option in BASIC_NEO4J_OPTIONS:
    NEO4J_OPTIONS[option] = option


def propertysetter(func):
    return property(fset=func, doc=func.__doc__)

class BaseAdminInterface(object):
    @classmethod
    def config(AdminInterface, parameters):
        config = {}
        for key in dir(AdminInterface):
            value = parameters.pop(key, None)
            if value is not None:
                config[key] = value
        return config
    def __init__(self, neo, config, log):
        self.__neo = neo
        self.__log = log
        self.__lock = threading.Lock()
        for key, value in config.items():
            setattr(self, key, value)
    def __str__(self):
        return "GraphDatabaseAdmin[implementation='%s']"%(self.implementation,)
    def _all_data_sources(self):
        raise NotImplementedError("Not supported by %s" % (self,))
    @propertysetter
    def keep_logical_logs(self, value):
        if value is None:
            try:
                value = self.__keep_logical_logs
            except:
                return
        assert isinstance(value, bool),\
            "graphdb.admin.keep_logical_logs = True/False"
        self.__keep_logical_logs = value
        for source in self._all_data_sources():
            if self.__log: self.__log.debug("%s.keep_logical_logs = %s",
                                            source, value)
            source.keepLogicalLogs( value )
    @propertysetter
    def auto_rotate_logs(self, value):
        for source in self._all_data_sources():
            source.setAutoRotate( True )
    def rotate_logical_logs(self):
        versions = []
        self.__lock.acquire() # with statement would give better performance...
        try:
            for source in self._all_data_sources():
                if self.__log: self.__log.debug("Rotating logs on %s.", source)
                versions.append( (source, source.getCurrentLogVersion()) )
                source.rotateLogicalLog()
        finally:
            self.__lock.release()
        result = []
        for source,version in versions:
            try:
                result.append(source.getFileName(version))
            except:
                result.append( (str(source), version) )
        return result
    @property
    def implementation(self):
        if self.__class__ == BaseAdminInterface:
            return "<unknown>"
        return self.__module__.split('.')[-1]
    @property
    def number_of_nodes(self):
        raise NotImplementedError("Cannot get the number of nodes")
    @property
    def number_of_relationships(self):
        raise NotImplementedError("Cannot get the number of relationships")
    @property
    def number_of_relationship_types(self):
        raise NotImplementedError("Cannot get the number of relationship types")


def load_neo(resource_uri, parameters):
    global load_neo,\
        NotFoundError, NotInTransactionError, DeadlockDetectedError, Traversal,\
        Incoming, Outgoing, Undirected, BREADTH_FIRST, DEPTH_FIRST,\
        RETURN_ALL_NODES, RETURN_ALL_BUT_START_NODE,\
        STOP_AT_END_OF_GRAPH, StopAtDepth
    import neo4j
    import neo4j._backend as backend
    import neo4j._primitives as primitives
    import neo4j._traverse as traversals
    import neo4j._index as indexes
    import os.path, atexit
    log = parameters.get('log', None)
    if isinstance(log, bool) and log is True:
        import logging
        parameters['log'] = log = logging # use base logger
    elif is_string(log) or is_integer(log):
        import logging
        logger = logging.getLogger("neo4j")
        logger.setLevel(log)
        if not logger.handlers:
            import sys
            logger.addHandler(logging.StreamHandler(sys.stdout))
        parameters['log'] = log = logger
    # Setup the parameters
    class_base = os.path.join(os.path.dirname(__file__), 'classes')
    if 'classpath' not in parameters:
        parameters['classpath'] = classpath = []
        if os.path.isdir(class_base):
            for file in os.listdir(class_base):
                classpath.append(os.path.join(class_base, file))
    elif isinstance(parameters['classpath'], basestring):
        parameters['classpath'] = parameters['classpath'].split(os.pathsep)
    if 'ext_dirs' not in parameters: # JPype cannot handle jars on classpath
        if os.path.isdir(class_base):
            parameters['ext_dirs'] = [class_base]
    elif isinstance(parameters['ext_dirs'], basestring):
        parameters['ext_dirs'] = parameters['ext_dirs'].split(os.pathsep)
    if log:
        log.debug("classpath is: %s", parameters['classpath'])
        log.debug("ext_dirs is:  %s", parameters['ext_dirs'])
    # TODO: implement support for read_only GraphDatabase
    if parameters.get('read_only', False):
        raise NotImplementedError("read_only mode")
    # Load the backend and the Neo4j classes
    backend.initialize(**parameters)
    # Initialize subsystems
    primitives.initialize(backend.implementation)
    traversals.initialize(backend.implementation)
    indexes.initialize(backend.implementation)
    # Define the namespace
    Node, Relationship        = primitives.Node, primitives.Relationship
    Traversal                 = traversals.Traversal
    NotFoundError             = backend.implementation.NotFoundException
    NotInTransactionError     = backend.implementation.NotInTransactionException
    DeadlockDetectedError     = backend.implementation.DeadlockDetectedException
    Incoming                  = traversals.Incoming
    Outgoing                  = traversals.Outgoing
    Undirected                = traversals.Undirected
    BREADTH_FIRST             = backend.implementation.BREADTH_FIRST
    DEPTH_FIRST               = backend.implementation.DEPTH_FIRST
    RETURN_ALL_NODES          = backend.implementation.ALL
    RETURN_ALL_BUT_START_NODE = backend.implementation.ALL_BUT_START_NODE
    STOP_AT_END_OF_GRAPH      = backend.implementation.END_OF_GRAPH
    StopAtDepth               = backend.implementation.StopAtDepth
    try:
        AdminInterface        = backend.implementation.AdminInterface
    except:
        AdminInterface        = BaseAdminInterface
    # Define replacement load function for use when the initial load is done
    def load_neo(resource_uri, parameters):
        log = parameters.get('log', None)
        settings = {}
        config = AdminInterface.config(parameters)
        for in_key, out_key in NEO4J_OPTIONS.items():
            value = parameters.get(in_key)
            if value is not None:
                settings[out_key] = value
        if parameters.get('start_server', False):
            server_path = parameters.get('server_path', resource_uri)
            if '://' in server_path:
                if server_path.startswith('file://'):
                    server_path = server_path[7:]
                else:
                    server_path = None
            if server_path is not None:
                if log: log.info("Starting Neo4j server for "
                                 "resource_uri=%r at server_path=%r",
                                 resource_uri, server_path)
                backend.start_server(resource_uri, server_path)
        return GraphDatabase(resource_uri, settings, config, log)
    # Define the implementation
    # --- <GraphDatabase> ---
    class GraphDatabase(Neo4jObject):#Use same name everywhere for name mangling
        def __init__(self, resource_uri, settings, config, log):
            neo = backend.load_neo(resource_uri, settings)
            Neo4jObject.__init__(self, neo=neo)
            self.__neo = neo
            self.__admin = admin = AdminInterface(neo, config, log)
            self.__nodes = NodeFactory(self, neo, admin)
            self.__relationships = RelationshipLookup(self, neo, admin)
            self.__index = indexes.IndexService(self, neo)
            self.__transaction = lambda: TransactionContext(neo)
            self.__log = log
            atexit.register(self.shutdown)
        def __getattr__(self, attr):
            if attr.lower() in ('ref', 'reference',
                                'referencenode', 'reference_node'):
                return self.reference_node
            else:
                raise AttributeError("GraphDatabase has no attribute '%s'"%attr)
    body = {'__doc__': neo4j.GraphDatabase.__doc__}
    for name in dir(neo4j.GraphDatabase):
        if not name.startswith('_'):
            member = getattr(neo4j.GraphDatabase, name)
            if isinstance(member, property):
                pass
            elif hasattr(member, 'im_func'):
                member = member.im_func
            elif hasattr(member, '__func__'):
                member = member.__func__
            body[name] = member
    GraphDatabase = type("GraphDatabase", (GraphDatabase,), body)
    # --- </GraphDatabase> ---
    if hasattr(backend.implementation, 'tx_join'):
        if log: log.debug("Transaction joining in effect "
                          "(mechanism used to discover threads).")
        tx_join = backend.implementation.tx_join
    else:
        tx_join = None
    class TransactionContext(object):
        def __init__(self, neo):
            self.__neo = neo
            self.__tx = None
        if tx_join is None:
            def begin(self):
                if self.__tx is None:
                    self.__tx = self.__neo.beginTx()
                return self
        else:
            def begin(self):
                tx_join()
                if self.__tx is None:
                    self.__tx = self.__neo.beginTx()
                return self
        def success(self):
            if self.__tx is not None:
                self.__tx.success()
        def failure(self):
            if self.__tx is not None:
                self.__tx.failure()
        def finish(self):
            if self.__tx is not None:
                self.__tx.finish()
            self.__tx = None
        __enter__ = __call__ = begin
        def __exit__(self, type=None, value=None, traceback=None):
            if self.__tx is not None:
                if type is None:
                    self.__tx.success()
                else:
                    self.__tx.failure()
                self.__tx.finish()
                self.__tx = None
    class NodeFactory(object):
        def __init__(self, neo, backend, admin):
            self.__neo = neo
            self.__backend = backend
            self.__admin = admin
        def __len__(self):
            return self.__admin.number_of_nodes
        def __getitem__(self, id):
            return Node(self.__neo, self.__backend.getNodeById(id))
        def __call__(self, **attributes):
            node = Node(self.__neo, self.__backend.createNode())
            for key, value in attributes.items():
                node[key] = value
            return node
        @property
        def reference(self):
            return Node(self.__neo, self.__backend.getReferenceNode())
    class RelationshipLookup(object):
        def __init__(self, neo, backend, admin):
            self.__neo = neo
            self.__backend = backend
            self.__admin = admin
        def __len__(self):
            return self.__admin.number_of_relationships
        def __getitem__(self, id):
            return Relationship(self.__neo,
                                self.__backend.getRelationshipById(id))
    import neo4j._hooks as hooks
    hooks.initialize(parameters)
    return load_neo(resource_uri, parameters)
