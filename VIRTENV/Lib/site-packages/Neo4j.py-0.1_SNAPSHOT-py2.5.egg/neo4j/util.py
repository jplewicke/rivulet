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
Utility functions that make working with Neo4j in Python easier.

 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

from __future__ import with_statement

def Subreference():
    global Subreference

    class AttributeInstance(type):
        def __getattr__(cls, attr):
            self = Subreference.__new__(cls, attr)
            setattr(cls, attr, self)
            return self

    def DontInstantiate(cls, *args, **kwargs):
        raise TypeError("%s cannot be instanciated." % (cls.__name__,))

    class Subreference(object):
        def __new__(cls, reltype):
            if cls is Subreference: raise TypeError(
                "Subreference cannot be instanciated.")
            self = object.__new__(cls)
            self.__reltype = reltype
            return self
        
        def __call__(self, graphdb, node=None, **properties):
            with graphdb.transaction:
                if node is None: node = graphdb.reference_node
    
                for rel in node.relationships(self.__reltype):
                    item = self.select(rel, rel.getOtherNode(node))
                    for key, value in properties.items():
                        if item[key] != value: break
                    else:
                        break
                else:
                    sub = graphdb.node()
                    mkrel = node.relationships(self.__reltype)
                    item = self.select(mkrel(sub), sub)
                    item.update(properties)
    
                return item
    
    class SubreferenceNode(Subreference):
        __metaclass__ = AttributeInstance
        __new__ = DontInstantiate
        def select(self, relationship, node):
            return node
    
    class SubreferenceRelationship(Subreference):
        __metaclass__ = AttributeInstance
        __new__ = DontInstantiate
        def select(self, relationship, node):
            return relationship
    
    Subreference.Node = SubreferenceNode
    Subreference.Relationship = SubreferenceRelationship

Subreference()
