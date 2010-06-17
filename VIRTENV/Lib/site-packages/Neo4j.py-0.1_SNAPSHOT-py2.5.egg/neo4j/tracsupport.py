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
This module defines points for integrating with Neo4j from trac.


 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""
### TODO: Documentation! ###

from __future__ import with_statement

import os

__all__ = 'GraphDatabaseProperty',

def __body__():
    global GraphDatabaseProperty#, ModelFactory
    import os.path
    try:
        from trac.core import Component, implements, Interface, ExtensionPoint
        from trac.config import ListOption, BoolOption, PathOption, Option
    except:
        return
    import neo4j

    KEY = "Trac project environment"

    def normalize_path(base, path):
        if not os.path.isabs(path):
            path = os.path.join(base, path)
        return os.path.normcase(os.path.realpath(path))

    class TracNeo(object):
        def __init__(self, env, neo):
            self.env = env
            self.neo = neo
            with neo.transaction:
                for rel in neo.reference_node.relationships(KEY).outgoing:
                    if rel[KEY] == env.path:
                        root = rel.end
                        break
                else:
                    root = neo.node()
                    neo.reference_node.relationships(KEY)(
                        root, **{KEY:env.path})
            self.root = root
        def index(self, name, **options):
            return self.neo.index("%s-%s" % (self.root.id, name), **options)
        def __getattr__(self, attr):
            return getattr(self.neo, attr)

    class IGraphDatabaseProvider(Interface):
        def instance(resource_uri, params): pass

    class Options(list):
        def add(self, option, filter=(lambda x:x)):
            self.append((option.name, filter))
            return option

    class ServiceProvider(Component):
        implements(IGraphDatabaseProvider)

        resource_uri = Option('neo4j','resource_uri', doc="""
""")
        options = Options()
        classpath = options.add(ListOption('neo4j','classpath', sep=os.pathsep,
                                           doc="""
"""))
        ext_dirs = options.add(ListOption('neo4j','ext_dirs', sep=os.pathsep,
                                          doc="""
"""))
        start_server = options.add(BoolOption('neo4j','start_server', doc="""
"""))
        server_path = options.add(PathOption('neo4j','server_path', doc="""
"""))
        username = options.add(Option('neo4j','username', doc="""
"""))
        password = options.add(Option('neo4j','password', doc="""
"""))
        jvm = options.add(PathOption('neo4j','jvm', doc="""
"""))

        def start(self, resource_uri, params):
            if resource_uri is None:
                resource_uri = self.resource_uri
                if not resource_uri:
                    resource_uri = os.path.join(self.env.path, 'neodb')
            if resource_uri.startswith('file://'):
                resource_uri = 'file://' + normalize_path(
                    self.env.path, resource_uri[7:])
            elif '://' not in resource_uri:
                resource_uri = normalize_path(self.env.path, resource_uri)
            for option, filter in self.options:
                if option not in params:
                    value = getattr(self, option)
                    if value is not None:
                        params[option] = filter(value)
            return resource_uri, neo4j.GraphDatabase(resource_uri, **params)

        instances = {}
        def instance(self, resource_uri, params):
            if resource_uri not in self.instances:
                key = resource_uri
                resource_uri, neo = self.start(resource_uri, params)
                neo = TracNeo(self.env, neo)
                if resource_uri != key:
                    self.instances[resource_uri] = neo
                self.instances[key] = neo
            return self.instances[resource_uri]

    def GraphDatabaseProperty(resource_uri=None, **params):
        """Documentation goes here..."""
        ep = ExtensionPoint(IGraphDatabaseProvider)
        def GraphDatabaseProperty(component):
            for neo_service in ep.extensions(component):
                return neo_service.instance(resource_uri, params)
        return property(GraphDatabaseProperty)

    class ModelFactory(object): # XXX: Not ready yet
        def __init__(self):
            pass
        def __get__(self, object, cls):
            if object is None: # Class accessor
                return None
            else: # Object accessor
                return None

__body__(); del __body__
