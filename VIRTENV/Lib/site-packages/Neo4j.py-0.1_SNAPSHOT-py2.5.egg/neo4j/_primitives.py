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
Primitive elements in Neo4j.py

 There are two main datatypes in Neo4j, Nodes and Relationships.

 Both Nodes and Relationships can have properties. Properties are mappings
 from a string key to a value. The value can be a number, a string, an array
 of numbers or an array of strings.

 The properties of both nodes and relationships are accessed as if the
 node/relationship was a dict in Neo4j.py. Not all methods of the dict
 type are implemented, but all protocols that the dict support are
 implemented.


 Copyright (c) 2008-2010 "Neo Technology,"
    Network Engine for Objects in Lund AB {{http://neotechnology.com}}
"""

class _PropertyDict(object): # NOTE: Should this inherit from dict?
    """An implementation of the dict interface for storeing properties.
    This is the base class for Node and Relation."""
    def __init__(self, owner):
        self.__get  = owner.getProperty
        self.__set  = owner.setProperty
        self.__has  = owner.hasProperty
        self.__del  = owner.removeProperty
        self.__keys = owner.getPropertyKeys
        self.__vals = owner.getPropertyValues
        self.__id   = owner.getId
    @property
    def id(self):
        """The native id of this primitive."""
        return self.__id()

    def __getitem__(self,item):
        """s.__getitem__(p) <=> s[p]"""
        return self.__get(item)
    def __setitem__(self,item,value):
        """s.__setitem__(p,v) <=> s[p] = v"""
        self.__set(item, value)
    def __delitem__(self,item):
        """s.__delitem__(p) <=> del s[p]"""
        self.__del(item)
    def __contains__(self,item):
        """s.__contains__(p) <=> p in s <=> s.has_key(p)"""
        return self.__has(item)

    def __iter__(self):
        """s.__iter__() <=> iter(s) <=> s.iterkeys()"""
        return self.iterkeys()
    def __len__(self):
        """s.__len__() <=> len(s)
        Returns the number of properties in s."""
        return len( self.keys() )
    
    def get(self,key,default=None):
        """<<<s.get(p[,d]) -> s[p] if p in s else d.>>>"""
        if key in self:
            return self[key]
        else:
            return default

    def items(self):
        """s.items() -> list of s's property (key, value) pairs, as 2-tuples."""
        return [item for item in self.iteritems()]
    def iteritems(self):
        """s.iteritems() -> an iterator over the property (key, value) items
        of s."""
        for key in self:
            yield key, self[key]
    def keys(self):
        """s.keys() -> list of s's property keys."""
        return [key for key in self.iterkeys()]
    def iterkeys(self):
        """s.iterkeys() -> an iterator over the property keys in s."""
        return iter(self.__keys())
    def values(self):
        """s.values() -> list of s's property values."""
        return [value for value in self.itervalues()]
    def itervalues(self):
        """s.itervalues() -> an iterator over the property values in s."""
        return iter(self.__vals())

    def setdefault(self, key, default=None):
        """s.setdefault(k[,d]) -> s.get(k,d), also set s[k]=d if k not in s"""
        if key in self:
            return self[key]
        elif default is not None:
            self[key] = default
        return default

    def update(self,*args,**more):
        """s.update(E, **F) -> None.  Update s from E and F:
        if hasattr(E,'keys'):
            for k in E: s[k] = E[k] 
        else:
            for (k, v) in E: s[k] = v
        Then:
        for k in F:
            s[k] = F[k]
        """
        if not len(args) in (0,1):
            raise TypeError("Too many arguments.")
        if args:
            for key,value in args[0].iteritems():
                self[key] = value
        for key,value in more.iteritems():
            self[key] = value


class Node(_PropertyDict):
    """Represents a Node...

 The properties of a node are accessed using subscript, like so:

------------------------------------------
property_value = node['property key']
node['property key'] = 'a string value'
node['other key']    = 42
del node['some key'] # remove the property
------------------------------------------

 Relationships are accessed using attributes:

--------------------------------------------------------
for relationship in node.SOME_RELATIONSHIP_TYPE:
    # do something

single_relationship = node.SOME_RELATIONSHIP_TYPE.single
--------------------------------------------------------

 Creating relationships is done by simply invoking the relationship accessor:

----------------------------------------------------------
new_relationship = node.SOME_RELATIONSHIP_TYPE(other_node)

# it is also possible to specify relationship properties:
new = node.knows(other, time=14, time_unit="days")
----------------------------------------------------------

 Single relationships can also be created by assigning a node:

-----------------------------------------------
node.SOME_RELATIONSHIP_TYPE.single = other_node
-----------------------------------------------

 This does not allow for the addition of properties, but since there
 is only a single relationship it is easy accessed, or even removed:

-------------------------------------------------
the_relation = node.SOME_RELATIONSHIP_TYPE.single
the_relation['property i forgot'] = 17
del node.SOME_OTHER_RELATIONSHIP_TYPE.single
-------------------------------------------------

 Normally when accessing relationships both incoming and outgoing
 relationships are accessed, to restrict this the <<<incoming>>> and
 <<<outgoing>>> modifiers can be used:

------------------------------------------------
for outgoing_relation in node.REL_TYPE.outgoing:
    # do stuff
for incoming_relation in node.REL_TYPE.incoming:
    # do other stuff

single_incoming = node.REL_TYPE.incoming.single
------------------------------------------------
"""
    def relationships(self, *types):
        """Return all relationships of any of the specified types.

 <<Usage:>>

---------------------------------------------------------------
for relationship in node.relationships('TYPE_ONE', 'TYPE_TWO'):
    # do something with the relationship
---------------------------------------------------------------
"""

def initialize(backend):
    global Node, Relationship
    INCOMING = backend.INCOMING
    OUTGOING = backend.OUTGOING
    BOTH = backend.BOTH
    RelationshipType = backend.RelationshipType
    from neo4j._base import Neo4jObject,\
        node as get_node, relationship as get_relationship
    class Node(_PropertyDict, Neo4jObject):
        __doc__ = Node.__doc__
        def __init__(self, neo, node):
            Neo4jObject.__init__(self, neo=neo, node=node)
            _PropertyDict.__init__(self, node)
            self.__neo = neo
            self.__node = node
        def __eq__(self, other):
            try:
                return self.__node.getId() == other.__node.getId()
            except:
                return False
        def __repr__(self):
            return '<Node id=%s>' % (self.id,)
        def __hash__(self):
            return self.id
        def __getattr__(self, attr):
            return self.relationships(attr)
        def relationships(self, *types):
            """Documentation for this is on module level - keep API in sync."""
            rel_types = []
            for type in types:
                rel_types.append(RelationshipType(type))
            return RelationshipFactory(self.__neo, self.__node, BOTH, rel_types)
        def delete(self):
            self.__node.delete()
        relationships.__doc__ = Node.relationships.__doc__
    
    class RelationshipFactory(object):
        def __init__(self, neo, node, dir, types):
            self.__neo = neo
            self.__node = node
            self.__dir = dir
            self.__types = types
            if len(types) == 1:
                self.__single_type = types[0]
            else:
                self.__single_type = None
        def __getRelationships(self):
            if not self.__types:
                for rel in self.__node.getRelationships(self.__dir):
                    yield rel
            elif len(self.__types) > 1:
                for type in self.__types:
                    for rel in self.__node.getRelationships(type, self.__dir):
                        yield rel
            else:
                for rel in self.__node.getRelationships(self.__single_type,
                                                        self.__dir):
                    yield rel
        def __hasRelationship(self):
            if not self.__types:
                return self.__node.hasRelationship(self.__dir)
            elif len(self.__types) > 1:
                for type in self.__types:
                    if self.__node.hasRelationship(type, self.__dir):
                        return True
                return False
            else:
                return self.__node.hasRelationship(self.__single_type,
                                                   self.__dir)
        def __single(self):
            if not self.__single_type:
                raise TypeError("No single relationship type!")
            return self.__node.getSingleRelationship(self.__single_type,
                                                     self.__dir)
        def __call__(self, node, **attributes):
            node = get_node(node)
            if self.__dir is INCOMING:
                relationship = node.createRelationshipTo(
                    self.__node, self.__single_type)
            else:
                relationship = self.__node.createRelationshipTo(
                    node, self.__single_type)
            relationship = Relationship(self.__neo, relationship)
            relationship.update(attributes)
            return relationship
        def __iter__(self):
            for rel in self.__getRelationships():
                yield Relationship(self.__neo, rel)
        def __nonzero__(self):
            return self.__hasRelationship()
        # - single relationship property -
        def get_single(self):
            single = self.__single()
            if single:
                return Relationship(self.__neo, single)
            else:
                return None
        def set_single(self, node):
            del self.single
            self(node)
        def del_single(self):
            single = self.__single()
            if single: single.delete()
        single = property(get_single, set_single, del_single)
        del get_single, set_single, del_single
        @property
        def incoming(self):
            return RelationshipFactory(self.__neo, self.__node,
                                       INCOMING, self.__types)
        @property
        def outgoing(self):
            return RelationshipFactory(self.__neo, self.__node,
                                       OUTGOING, self.__types)
    
    class Relationship(Relationship, Neo4jObject):
        def __init__(self, neo, relationship):
            Neo4jObject.__init__(self, neo=neo, relationship=relationship)
            _PropertyDict.__init__(self, relationship)
            self.__relationship = relationship
            self.__neo = neo
        def __eq__(self, other):
            try:
                return self.__relationship.getId()==other.__relationship.getId()
            except:
                return False
        def __repr__(self):
            return '<Relationship type=%r id=%s>' % (self.type, self.id)
        def __hash__(self):
            return self.id
        def getOtherNode(self, node):
            """Documentation for this is on module level - keep API in sync."""
            node = get_node(node)
            return Node(self.__neo, self.__relationship.getOtherNode(node))
        def delete(self):
            self.__relationship.delete()
        getOtherNode.__doc__ = Relationship.getOtherNode.__doc__

class Relationship(_PropertyDict):
    """Represents a Relationship..."""
    @property
    def start(self):
        """The start node of the relationship."""
        return Node(self.__neo, self.__relationship.getStartNode())
    @property
    def end(self):
        """The end node of the relationship."""
        return Node(self.__neo, self.__relationship.getEndNode())
    @property
    def type(self):
        """The type of the relationship (as a string)."""
        return self.__relationship.getType().name()
    def getOtherNode(self, node):
        """Given one node that participates in a relationship, return the other.

 <<Usage:>>

----------------------------------------------------
other = node.SOME_RELATION.single.getOtherNode(node)
----------------------------------------------------
"""
