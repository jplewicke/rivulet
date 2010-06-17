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
Hooks into other systems, for automatically exporting Neo4j.py as persistence
backend for various systems.


 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

def initialize(parameters):
    # Try to add Neo as a backend for RDFLib
    try:
        from rdflib import plugin
        from rdflib.store import Store
        import neo4j._rdf # assert that the RDF subsystem is available
    except: # requirements failed, don't register the hook
        pass
    else: # register the hook
        plugin.register('Neo', Store, 'neo4j._hooks.rdflib', 'NeoRdfStore')
