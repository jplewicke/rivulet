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
Neo4j.py Traversal API

 Traversers are objects that iterates over the nodes in the nodespace, starting
 at a given node, according to two evaluator functions(/objects). The two
 evaluators are one that prunes the network (decides wheter the traverser should
 stop at a given position or continue) and one that decides which nodes should
 be yielded by the traverser.


 Copyright (c) 2008-2010 "Neo Technology,"
    Network Engine for Objects in Lund AB {{http://neotechnology.com}}
"""

from neo4j._base import primitives

def initialize(backend):
    global initialize, Traversal, Outgoing, Incoming, Undirected
    def initialize(backend): pass # should only be done once
    from neo4j._primitives import Node, Relationship
    from neo4j import Traversal
    RelationshipType = backend.RelationshipType
    def traverse(node, evaluator):
        # NOTE: This API is a bit ugly, but at least we hide it nicely.
        #       If it is changed, this function needs to be updated.
        traverser = node.traverse(evaluator.order,
                                  evaluator.stop,
                                  evaluator.returnable,
                                  evaluator.types)
        iterator = traverser.iterator()
        while iterator.hasNext():
            iterator.next()
            yield traverser.currentPosition()
    class Evaluator(backend.Evaluator):
        def __init__(self, neo, traversal):
            super(Evaluator, self).__init__()
            self.__neo = neo
            self.traversal = traversal
            self.order = traversal.order
            types = []
            for type in get_types(traversal):
                types.append(RelationshipType(type.type))
                types.append(type.direction)
            self.types = backend.array(types)
            # Superclass defines these as dispatchers to the methods bellow:
            if not hasattr(traversal, 'isStopNode'):
                self.stop = traversal.stop
            if not hasattr(traversal, 'isReturnable'):
                self.returnable = traversal.returnable
        def isStopNode(self, pos):
            return self.traversal.isStopNode(
                TraversalPosition(self.__neo, pos))
        def isReturnableNode(self, pos):
            return self.traversal.isReturnable(
                TraversalPosition(self.__neo, pos))
    class TraversalNode(Node):
        def __init__(self, neo, pos):
            Node.__init__(self, neo, pos.currentNode())
            self.depth = pos.depth()
    class TraversalPosition(TraversalNode):
        def __init__(self, neo, pos):
            TraversalNode.__init__(self, neo, pos)
            self.__pos = pos
            self.__neo = neo
            self.returned_count = pos.returnedNodesCount()
        @property
        def is_start(self):
            return bool(self.__pos.isStartNode())
        @property
        def last_relationship(self):
            if self.is_start: return None
            return Relationship(self.__neo,
                                self.__pos.lastRelationshipTraversed())
        @property
        def previous_node(self):
            return Node(self.__neo, self.__pos.previousNode())
    def __iter__(self):
        neo, node, _ = primitives(self._Traversal__start) # Manual mangling
        for position in traverse(node, Evaluator(neo, self)):
            yield TraversalNode(neo, position)
    Traversal.__iter__ = __iter__
    def get_types(traversal, accessor=Traversal._traversal_types_):
        return accessor.__get__(traversal)
    del Traversal._traversal_types_
    class DirectedType(object):
        def __init__(self, direction, type):
            self.direction = direction
            self.type = type
    class Direction(object):
        def __init__(self, dir):
            self.__direction = dir
        def __call__(self, type):
            return DirectedType(self.__direction, type)
        def __getattr__(self, attr):
            return self(attr)
    Outgoing = Direction(backend.OUTGOING)
    Incoming = Direction(backend.INCOMING)
    Undirected = Direction(backend.BOTH)
