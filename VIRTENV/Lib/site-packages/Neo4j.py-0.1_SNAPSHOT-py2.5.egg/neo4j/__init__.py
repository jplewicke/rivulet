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
Neo4j.py   --   Python bindings for the Neo4j Graph Database

 A Python wrapper for Neo4j {{http://neo4j.org/}}

 Website: {{http://components.neo4j.org/neo4j.py/}}

 Neo4j.py can be used either with Jython or with JPype or JCC in CPython.
 Neo4j.py is used in exactly the same way regardless of which backend is
 used.

 The typical way to use Neo4j.py is:

------------------------------------------------------------
import neo4j
graphdb = neo4j.GraphDatabase( "/neo/db/path" )
with graphdb.transaction:
    ref_node = graphdb.reference_node
    new_node = graphdb.node()
    # put operations that manipulate the node space here ...
graphdb.shutdown()
------------------------------------------------------------

* Getting started

** Requirements

 In order to use Neo4j.py, regardless of whether Jython or CPython is used
 the system needs to have a JVM installed.

 The required Java classes are automatically downloaded and installed as
 part of the installation process.

** With CPython

 To use Neo4j.py with CPython the system needs to have JPype
 {{http://jpype.sourceforge.net/}} installed.

 To install Neo4j.py simply check out the source code:

-----------------------------------------------------------------------
svn export https://svn.neo4j.org/components/neo4j.py/trunk neo4j-python
-----------------------------------------------------------------------

 Then install using distutils:

----------------------------
sudo python setup.py install
----------------------------

 This requires connection to the internet since it will download the
 required java libraries.

** With Jython

 Check out and install as with CPython:

-----------------------------------------------------------------------
svn export https://svn.neo4j.org/components/neo4j.py/trunk neo4j-python
cd neo4j-python
sudo jython setup.py install
-----------------------------------------------------------------------

** Windows installation issues

 Jython (in 2.5b3 or earlier) has a problem with installing packages under
 Windows. You might get this error when installing:

-----------------------------------------------------------------------------
running install_egg_info
Creating X:\\<PATH_TO>\\jython\\Lib\\site-packages\\
error: X:\\<PATH_TO>\\jython\\Lib\\site-packages\\: couldn't make directories
-----------------------------------------------------------------------------

 If the install output ends like that when installing under Windows,
 don't panic.

 All of Neo4j.py has already been installed at this point. This can be
 verified by checking that
 <<X:\\<PATH_TO>\\jython\\Lib\\site-packages\\neo4j>> contains some
 directories, Python source files and bytecode compiled files. You can also
 verify that
 <<X:\\<PATH_TO>\\jython\\Lib\\site-packages\\neo4j\\classes>>
 contains the required jar-files. What the install script has failed to do
 is to write the package information. This may cause trouble when
 installing a new version of neo4j.py, the fix for this is to manually
 remove neo4j.py before installing a new version.

 This issue has been reported at {{https://trac.neo4j.org/ticket/156}} and
 {{http://bugs.jython.org/issue1110}}. We have fixed this for the next
 release of Jython.

** JPype installation issues

 In some situations the JPype compilation process might not link with the
 appropriate JNI headers, resulting in compilation errors.

 The first thing to note is that JPype needs the JNI headers from a JDK
 in order to build, it is not enough to only have a JRE installed when
 building JPype.

 If the JAVA_HOME environment variable is not set when building JPype the
 build script (setup.py) of JPype might have problems locating the
 appropriate JNI headers.

 If you are building JPype with <<sudo python setup.py install>> you might
 not inherit the JAVA_HOME environment variable into the sudo environment,
 an easy warkaround is to run <<python setup.py bdist>> before install.

 For more information see the following resources:

 * {{http://sourceforge.net/mailarchive/forum.php?thread_name=1afed6d30907300541v74a722c0nbf9155832affd101%40mail.gmail.com&forum_name=jpype-users}}

** Starting the Neo4j Graph Database

 Apart from specifying the path to where the Neo4j graph data is stored to
 GraphDatabase a few extra keyword options may be specified. These include:

    [classpath] A list of paths that are to be added to the classpath
                in order to be able to find the Java classes for Neo4j.
                This defaults to the jar files that were installed with
                this package.

    [ext_dirs ] A list of paths to directories that contain jar files
                that in turn contains the Java classes for Neo4j.
                This defaults to the jar file directory that was installed
                with this package.
                The <<classpath>> option is used before <<ext_dirs>>.

    [jvm      ] The path to the JVM to use. This is ignored when using
                Jython since Jython is already running inside a JVM.
                Neo4j.py is usualy able to compute this path.

 <<Note>> that if the Neo4j Java classes are available on your system
 classpath the classpath and ext_dirs options will be ignored.

 <<Example:>>

----------------------------------------------------------------
graphdb = neo4j.GraphDatabase("/neo/db/path",
                              classpath=["/a/newer/kernel.jar"],
                              jvm="/usr/lib/jvm.so")
----------------------------------------------------------------

* Package content

 Some of the content of this package is loaded lazily. When the package is
 first imported The guaranteed content is GraphDatabase and the API required
 for defining Traversals, the Exceptions might not be available. When the
 first GraphDatabase has been initialized the rest of the package is loaded.

 The content of this module is:

    [GraphDatabase        ] factory for creating a Neo4j Graph Database.

    [Traversal            ] Base for defining traversals over the node
                            space.

    [NotFoundError        ] Exception that is raised when a node,
                            relationship or property could not be found.

    [NotInTransactionError] Exception that is raised when the node space
                            is manipulated outside of a transaction.

    << The rest of the content is used for defining Traversals >>

    [Incoming             ] Defines a relationship type traversable in the
                            incoming direction.

    [Outgoing             ] Defines a relationship type traversable in the
                            outgoing direction.

    [Undirected           ] Defines a relationship type traversable in any
                            direction.

    [BREADTH_FIRST        ] Defines a traversal in breadth first order.

    [DEPTH_FIRST          ] Defines a traversal in depth first order.

    [RETURN_ALL_NODES     ] Defines a traversal to return all nodes.

    [RETURN_ALL_BUT_START_NODE] Defines traversal to return all but first
                            node.

    [StopAtDepth(x)       ] Defines a traversal to only traverse to depth=x.

    [STOP_AT_END_OF_GRAPH ] Defines a traversal to traverse the entire
                            subgraph.

* Nodes, Relationships and Properties

 Creating a node:

------------------
n = graphdb.node()
------------------

 Specify properties for new node:

--------------------------------------------------
n = graphdb.node(color="Red", widht=16, height=32)
--------------------------------------------------

 Accessing node by id:

----------------------
n17 = graphdb.node[14]
----------------------

 Accessing properties:

----------------------------------------
value = e['key'] # get property value
e['key'] = value # set property value
del e['key']     # remove property value
----------------------------------------

 Create relationship:

------------
n1.Knows(n2)
------------

 Any name that does not mean anything for the node class can be used as
 relationship type:

----------------------------
n1.some_reltionship_type(n2)
n1.CASE_MATTERS(n2)
----------------------------

 Specify properties for new relationships:

---------------------------------------------
n1.Knows(n2, since=123456789,
             introduced_at="Christmas party")
---------------------------------------------

* Indexes

 Get index:

---
index = graphdb.index("index name")
---

 Create index:

------------------------------------------------
index = graphdb.index("some index", create=True)
------------------------------------------------

 If an index is created that already exists, the existing index will not be
 replaced, and the existing index will be returned. The create flag is a
 measure to help finding spelling errors in index names.

 Using indexes:

---------------------
index['value'] = node
node = index['value']
del index['value']
---------------------

 Keep in mind that when updating the index with a new value (f.ex. when a
 property value on a node changes) remember to remove the old value from the
 index as well, else both values will be indexed.

 Using indexes as multi value indexes:

--------------------------------------
multiIndex.add('value', node)
for node in multiIndex.nodes('value'):
    doStuffWith(node)
--------------------------------------

* Traversals

 Traversals are defined by creating a class that extends
 <<<neo4j.Traversal>>>, and possibly previously defined traversals as well.
 (Note that <<<neo4j.Traversal>>> always needs to be a direct parent of a
 traversal class.) A traversal class needs to define the following members:

    [types     ] A list of relationship types to be traversed in the
                 traversal. These are created using Incoming, Outgoing and
                 Undirected.

    [order     ] The order in which the nodes of the graph are to be
                 traversed. Valid values are BREADTH_FIRST and DEPTH_FIRST

    [stop      ] Definition of when the traversal should stop.
                 Valid values are STOP_AT_DEPTH_ONE and STOP_AT_END_OF_GRAPH
                 Alternatively the traversal class may define a more
                 advanced stop predicate in the form of a method called
                 'isStopNode'.

    [returnable] Definition of which nodes the traversal should yield.
                 Valid values are RETURN_ALL_NODES and
                 RETURN_ALL_BUT_START_NODE. Alternatively the traversal
                 class may define a more advanced returnable predicate in
                 the form of a method called 'isReturnable'.

 To define more advanced stop and returnable predicates the traversal class
 can define the methods 'isStopNode' and 'isReturnable' respectively.
 These methods should accept one argument (in addition to self), a traversal
 position. The position is essentially a node, but with the following extra
 properties:

    [last_relationship] The relationship that was traversed to reach this
                        node. This is None for the start node.

    [is_start         ] True if this is the start node, False otherwise.

    [previous_node    ] The node from which this node was reached.
                        This is None for the start node.

    [depth            ] The depth at which this node was found in the
                        traversal. This is 0 for the start node.

    [returned_count   ] The number of returned nodes so far.

 Nodes yielded by a traversal has an additional 'depth' attribute with the
 same semantics as above.

** Example Traversal declaration

------------------------------------------------------------------
class Hackers(neo4j.Traversal):
    types = [
        neo4j.Outgoing.knows,
        neo4j.Outgoing.coded_by,
        ]
    order = neo4j.DEPTH_FIRST
    stop = neo4j.STOP_AT_END_OF_GRAPH

    def isReturnable(self, position):
        return (not position.is_start
                and position.last_relationship.type == 'coded_by')

# Usage:
for hacker_node in Hackers(traversal_start_node):
    # do stuff with hacker_node
------------------------------------------------------------------

* Further information

 For more information about Neo4j, please visit {{http://neo4j.org/}}

 Please direct questions and discussions about Neo4j.py to the Neo4j
 mailing list: {{https://lists.neo4j.org/mailman/listinfo/user}}


 Copyright (c) 2008-2010 "Neo Technology,"
    Network Engine for Objects in Lund AB {{http://neotechnology.com}}
"""

if __name__.endswith('__init__'): raise ImportError # Prohibit import as module
__all__ = 'GraphDatabase', 'Traversal',

class GraphDatabase(object):
    # This class defines the API and implementation but is never instantiated
    # This class is instead redefined in the _core module.
    # Having the class defined here serves a documentation purpouse
    """This is the heart of Neo4j.

<<Usage:>>

----------------------------------------------------------------
graphdb = neo4j.GraphDatabase("/path/to/node_store/", **options)
----------------------------------------------------------------

* Accepted options

    [classpath] A list of paths to jar files or directories that contain
                Java class files.

    [ext_dirs ] A list of paths that contain jar files.

    [jvm      ] The path to the Java virtual machine to use.
                This option is not applicable with Jython and will be
                ignored.

    [heap_size] The size of the heap used by the JVM.
                This option is not applicable with Jython, but will be
                verified.

    [username ] The username to use when connecting to a remote server.

    [password ] The password to use when connecting to a remote server.

    [start_server] True if the remote server should be started.

    [server_path ] The path to where the server db is stored.

    [keep_logical_log] set this to True to keep logical logs after
                rotation. The logs will be renamed and stored instead
                of being removed after they have been rotated.

    The classpath or ext_dirs options are used for finding the Java
    implementation of Neo4j. If they are not specified it defaults to
    the jar files that are disributed with this package.

    The heap_size option is not available in Jython since the heap size
    is already specified when Jython is started. Neo4j will however
    verify that the current heap size is at least big enough to hold the
    size specified in this parameter, or issue a warning.
    """
    @property
    def transaction(self):
        """Access the transaction context for this GraphDatabase.

 <<Usage:>>

-------------------------
with graphdb.transaction:
    # do stuff...
-------------------------
        """
        return self.__transaction()
    def index(self, name, create=False, **options):
        """Access an index for this GraphDatabase.

 The name parameter is string containing the name of the
 index. If the create parameter is True the index is created
 if it does not exist already. Otherwise an exception is
 thrown for indexes that does not exist.

 <<Usage:>>

----------------------------------
name_index = graphdb.index('name')
----------------------------------
        """
        return self.__index.get(name, options, create)
    @property
    def node(self):
        """Access the nodes in this GraphDatabase.

 <<Usage:>>

-----------------------------------------------------------------------
node = graphdb.node[x] # lookup the node with id=x
node = graphdb.node()  # create a new node
node = graphdb.node(name="Thomas Anderson", # create a new node and set
                    age=27)           # the 'name' and 'age' properties
-----------------------------------------------------------------------
        """
        return self.__nodes
    @property
    def relationship(self):
        """Access the relationships in this GraphDatabase.

 <<Usage:>>

-----------------------------------------------------------------------
relationship = graphdb.relatoionship[x] # lookup relationship with id=x
-----------------------------------------------------------------------
        """
        return self.__relationships
    @property
    def admin(self):
        """Access the aministrative interface for this GraphDatabase.

 The actual content of the returned aministrative interface is
 implementation dependant and will have different members depending
 on the backend used by the Graph Database.

 The following members are guaranteed to always be part of the admin object:

    [implementation] The name of the backend used.
        """
        return self.__admin
    @property
    def reference_node(self):
        """Get the reference node for this GraphDatabase.
        
 <<Usage:>>

---------------------------------
ref_node = graphdb.reference_node
---------------------------------
        """
        return self.__nodes.reference
    def shutdown(self):
        """Shut down this GraphDatabase."""
        if self.__index is not None:
            self.__index.shutdown()
        if self.__neo is not None:
            self.__neo.shutdown()
    close = shutdown
    def __new__(cls, resource_uri, **params):
        global NotFoundError, NotInTransactionError, DeadlockDetectedError,\
            Traversal, Incoming, Outgoing, Undirected,\
            BREADTH_FIRST, DEPTH_FIRST,\
            RETURN_ALL_NODES, RETURN_ALL_BUT_START_NODE,\
            STOP_AT_END_OF_GRAPH, StopAtDepth
        from neo4j import _core as core
        neo = core.load_neo(resource_uri, params)
        # Store documentation
        doc_Traversal                 = Traversal.__doc__
        doc_Incoming                  = Incoming.__doc__
        doc_Outgoing                  = Outgoing.__doc__
        doc_Undirected                = Undirected.__doc__
        doc_StopAtDepth               = StopAtDepth.__doc__
        doc_BREADTH_FIRST             = BREADTH_FIRST.__doc__
        doc_DEPTH_FIRST               = DEPTH_FIRST.__doc__
        doc_RETURN_ALL_NODES          = RETURN_ALL_NODES.__doc__
        doc_RETURN_ALL_BUT_START_NODE = RETURN_ALL_BUT_START_NODE.__doc__
        doc_STOP_AT_END_OF_GRAPH      = STOP_AT_END_OF_GRAPH.__doc__
        # Define values for globals
        NotFoundError             = core.NotFoundError
        NotInTransactionError     = core.NotInTransactionError
        DeadlockDetectedError     = core.DeadlockDetectedError
        Traversal                 = core.Traversal
        Incoming                  = core.Incoming
        Outgoing                  = core.Outgoing
        Undirected                = core.Undirected
        StopAtDepth               = core.StopAtDepth
        BREADTH_FIRST             = core.BREADTH_FIRST
        DEPTH_FIRST               = core.DEPTH_FIRST
        RETURN_ALL_NODES          = core.RETURN_ALL_NODES
        RETURN_ALL_BUT_START_NODE = core.RETURN_ALL_BUT_START_NODE
        STOP_AT_END_OF_GRAPH      = core.STOP_AT_END_OF_GRAPH
        # Restore documentation
        try:
            Traversal.__doc__                 = doc_Traversal
            Incoming.__doc__                  = doc_Incoming
            Outgoing.__doc__                  = doc_Outgoing
            Undirected.__doc__                = doc_Undirected
            StopAtDepth.__doc__               = doc_StopAtDepth
            BREADTH_FIRST.__doc__             = doc_BREADTH_FIRST
            DEPTH_FIRST.__doc__               = doc_DEPTH_FIRST
            RETURN_ALL_NODES.__doc__          = doc_RETURN_ALL_NODES
            RETURN_ALL_BUT_START_NODE.__doc__ = doc_RETURN_ALL_BUT_START_NODE
            STOP_AT_END_OF_GRAPH.__doc__      = doc_STOP_AT_END_OF_GRAPH
        except:
            pass
        # Define replacement __new__
        @staticmethod
        def __new__(cls, resource_uri, **params):
            return core.load_neo(resource_uri, params)
        cls.__new__ = __new__
        return neo

def Traversal():
    global Traversal # Traversal base
    global Incoming, Outgoing, Undirected # Relationship directions
    global BREADTH_FIRST, DEPTH_FIRST # Traversal orders
    global RETURN_ALL_NODES, RETURN_ALL_BUT_START_NODE # Returnable conditions
    global StopAtDepth, STOP_AT_END_OF_GRAPH # Stop conditions

    class ReplaceProperty(object):
        def __init__(self, prop, doc):
            self.__doc__ = doc
            if isinstance(prop, str):
                self.__property = prop
            else:
                self.__getter = prop
                self.__property = prop.__name__
        def __get__(self, obj, cls=None):
            return self.__getter()
        def __getter(self):
            return globals()[self.__property]
        def __repr__(self):
            return self.__property

    class TraversalDirection(ReplaceProperty):
        def __getattr__(self, attr):
            return DirectedType(self, attr)

    class DirectedType(ReplaceProperty):
        def __init__(self, owner, attr):
            def __getter():
                return getattr(owner.__get__(None), attr)
            ReplaceProperty.__init__(self, __getter, "")
            self.type = attr
            self.direction = owner

    # Traversal directions

    Incoming = TraversalDirection('Incoming',
        doc="""Traverse incoming relationships (of the given type) only.
    """)
    Outgoing = TraversalDirection('Outgoing',
        doc="""Traverse outgoing relationships (of the given type) only.
    """)
    Undirected = TraversalDirection('Undirected',
        doc="""Traverse relationships (of the given type) in any direction.
    """)

    # Traversal order

    BREADTH_FIRST = ReplaceProperty('BREADTH_FIRST',
        doc="""Breadth first traversal order.
    """)
    DEPTH_FIRST = ReplaceProperty('DEPTH_FIRST',
        doc="""Depth first traversal order.
    """)

    # Returnable conditions

    RETURN_ALL_NODES = ReplaceProperty('RETURN_ALL_NODES',
        doc="""All traversed nodes are returned from the traversal.
    """)
    RETURN_ALL_BUT_START_NODE = ReplaceProperty('RETURN_ALL_BUT_START_NODE',
        doc="""All nodes except the start node are returned from the traversal.
    """)

    # Stop conditions

    class StopAtDepth(object):
        """Only traverse to a certain depth."""
        def __init__(self, depth):
            self.depth = depth
        def __get__(self, obj, cls=None):
            return globals()['StopAtDepth'](self.depth)
        def isStopNode(self, position):
            raise RuntimeError("Neo4j has not been initialized.")

    STOP_AT_END_OF_GRAPH = ReplaceProperty('STOP_AT_END_OF_GRAPH',
        doc="""End of graph stop condition.
    """)

    # Traversal

    class Traversal(object):
        """Base class for defining traversals.

 Traversals are defined as classes, with attributes defining:

 * Which relationships to traverse. The <<types>> attribute.

 * What order to traverse the nodes in. The <<order>> attribute.
   (the default value is breadth first)

 * When to stop traversing. Either by providing a stop evaluator as the
   <<stop>> attribute, or by defining a <<isStopNode>> method.

 * Which of the traversed nodes should be returned. Either by providing
   a returnable evaluator as the <<returnable>> attribute or by defining
   a <<isReturnable>> method.

 <<Example:>>

--------------------------------------
class Coworkers(neo4j.Traversal):
    types = [
        neo4j.Undirected.works_at,
        ]
   order = neo4j.BREADTH_FIRST
   stop = neo4j.StopAtDepth(2)
   def isReturnable(self, position):
       # the start node has depth == 0
       # the company has depth == 1
       # and coworkers have depth == 2
       return position.depth == 2
--------------------------------------

 To utilize a traversal you simply instantiate the class and iterate
 over the instance.

-------------------------------------------------
ted = get_the_node_that_represents_ted()
for coworker in Coworkers(ted):
    print( "Ted works with " + coworker['name'] )
-------------------------------------------------
        """
        @property
        def _traversal_types_(self):
            for type in self.types:
                if hasattr(type, '__get__'):
                    yield type.__get__(self)
                else:
                    yield type
        types      = ()
        order      = BREADTH_FIRST
        stop       = STOP_AT_END_OF_GRAPH
        returnable = RETURN_ALL_NODES
        def __init__(self, start):
            self.__start = start
        def __iter__(self):
            raise RuntimeError("Neo4j has not been initialized.")            

Traversal()

def transactional(accessor, **params):
    """Decorates a method so that it is executed within a transaction.

 The transactional function should be invoked with a single argument of a
 descriptor that returns an instance of GraphDatabase on __get__ (for example a
 property). The result of the transactional function is a method decorator that
 executes the decorated method within the context of a transaction on the
 GraphDatabase provided by the accessor descriptor.

 The transactional function accepts the optional keyword only argument retry.
 If retry is True the transactional operation will be retried if a deadlock
 is detected. Otherwise the operation will be attempted only once, and if
 a deadlock is detected a DeadlockDetectedError will be raised. The
 operation will only be retried when a deadlock is detected, other exceptional
 cases will still cause exceptions to be raised from the method.
 Retrying the operation means rolling back the transaction, starting a new
 transaction and re-execute the operation in that transaction.

 <<Example:>>

---------------------------------------------------------------------------
import neo4j

class MyService(object):
    def __init__(self, graphdb):
        self.__graphdb = graphdb
        for type_rel in graphdb.reference_node.data_type:
            if type_rel['type'] == 'MyEntity':
                self.__entities = type_rel.end
                break
        else:
            self.__entities = entities = graphdb.node()
            graphdb.reference_node.data_type(entities, type='MyEntity')

    @property
    def graphdb(self):
        # This is the descriptor used to get the GraphDatabase instance
        return self.__graphdb

    @neo4j.transactional(graphdb) # Make this method transactional
    def create_entity(self, name):
        node = self.graphdb.node(name=name)
        node.instance_of( self.__entities )
        return MyEntity( self.__graphdb, node )

class MyEntity(object):
    def __init__(self, graphdb, node):
        self.__graphdb
        self.__node = node

    @property
    def graphdb(self):
        # This is the descriptor used to get the GraphDatabase instance
        return self.__graphdb

    @property
    @neo4j.transactional(graphdb) # Make this property getter transactional
    def name(self):
        return self.__node['name']

    @name.setter
    @neo4j.transactional(graphdb) # Make this property setter transactional
    def name(self, name):
        self.__node['name'] = name
---------------------------------------------------------------------------
    """
    global transactional
    if transactional.__module__ == __name__:
        doc = transactional.__doc__
        try:
            from neo4j._util import transactional
        except:
            import sys
            raise NotImplementedError(
                "@transactional is not supported on Python %s." % '.'.join(
                    map(str, sys.version_info) ))
        else:
            transactional.__doc__ = doc
    return transactional(accessor, **params)

NeoService = GraphDatabase
