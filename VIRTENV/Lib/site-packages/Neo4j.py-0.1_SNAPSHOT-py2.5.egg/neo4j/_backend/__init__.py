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
This module selects the appropriate backend depending on platform.

 Copyright (c) 2008-2010 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

def initialize(classpath, **params):
    import sys
    global implementation, load_neo, start_server
    log = params.get('log', None)
    try: # Native implementation
        if 'java' in sys.platform.lower():
            if log: log.debug("Trying Jython backend.")
            from neo4j._backend import native as implementation
            embedded, remote = implementation.initialize(classpath, params)
            if log: log.debug("Using Jython backend.")
        elif 'cli' in sys.platform.lower():
            if log: log.debug("Trying IronPython backend.")
            from neo4j._backend import cli as implementation
            embedded, remote = implementation.initialize(classpath, params)
            if log: log.debug("Using IronPython backend.")
        else:
            try: # JCC
                if log: log.debug("Trying JCC backend.")
                from neo4j._backend import jcc as implementation
                embedded, remote = implementation.initialize(classpath, params)
                if log: log.debug("Using JCC backend.")
            except: # Fall back to JPype
                if log: log.debug("Trying JPype backend.")
                from neo4j._backend import reflection as implementation
                embedded, remote = implementation.initialize(classpath, params)
                if log: log.debug("Using JPype backend.")
    except:
        if log: log.error("Importing native backends failed.", exc_info=True)
        try: # Falling back to pure python implementation
            if log: log.debug("Trying pure Python backend.")
            from neo4j._backend import pure as implementation
            embedded, remote = implementation.initialize(classpath, params)
            if log: log.debug("Using pure Python backend.")
        except: # FAIL.
            raise ImportError("No applicable backend found.")
    # Define load function
    def load_neo(resource_uri, settings):
        if '://' not in resource_uri and embedded is not None:
            impl = embedded
        elif remote is not None:
            impl = remote
        elif resource_uri.startswith('file://') and embedded is not None:
            resource_uri = resource_uri[7:]
            impl = embedded
        else:
            raise RuntimeError("Cannot connect to Neo instance at '%s'." %
                               (resource_uri,))
        return impl(resource_uri, implementation.make_map(settings))
    def start_server(resource_uri, server_path):
        raise NotImplementedError("start_server is not implemented")
